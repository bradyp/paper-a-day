#!/usr/bin/perl -w
use warnings;
use strict;
use JSON;
use LWP;
use Encode;
use Digest::MD5 qw(md5_hex);

# Simple perl script to take a JSON object and insert it into the couchdb instance
# Assumptions are:
# 1. file given is a __valid__ JSON list of documents to insert.
# 2. each document has the following attributes (at a minimum):
#    id, abstract, title, references, keywords, citations, classification, docmetadata
# Currently there is a bug with the program which generates the JSON files for this where
# references and citations are both empty. docmetadata contains these, but references might have
# incomplete data for that. The update_citations_references subroutine attempts to correct these
# issues and populate the citations and references lists.
# 3. Added fields: source (currently "acm", but for support of additional sources)

my $host = "vertex.skizzerz.net";
my $port = 6984;
my $db = "papers";
my $options = {"ssl" => 1, "update_existing" => 1}; #add username and password keys for updating
#$options->{"username"} = "<username>";
#$options->{"password"} = "<password>";
#$ARGV[0] is the filename of the .json file
#add_docs($ARGV[0], $host, $port, $db, $options);
update_title($host, $port, $db, $options);
#update_citations_references($host, $port, $db, $options);

sub update_title {
	my($server, $port, $db, $options) = @_;
	my $json = JSON->new;
	my $ua = LWP::UserAgent->new;
	$ua->cookie_jar({});
	if(exists $options->{"ssl"} && $options->{"ssl"} && exists $options->{"ssl_verify_hostname"}
		&& $options->{"ssl_verify_hostname"} == 0)
	{
		$ua->ssl_opts("verify_hostname" => 0);
	}
	my $prot = (exists $options->{"ssl"} && $options->{"ssl"}) ? "https://" : "http://";
	my $path = (exists $options->{"path"} && $options->{"path"}) ? $options->{"path"} : "/";
	my $baseurl = $prot . $server . ":" . $port . $path;
	if(exists $options->{"username"} && $options->{"username"}
		&& exists $options->{"password"} && $options->{"password"})
	{
		# we need to modify baseurl to include name/password
		$baseurl = $prot . $options->{"username"} . ":" . $options->{"password"} . "@"
			. $server . ":" . $port . $path;
	}
	# grab the list of all documents in the db
	my $request = HTTP::Request->new("GET", $baseurl . $db . "/_design/missingdata/_view/title");
	my $response = $ua->request($request);
	if($response->code != 200) {
		print "Got error " . $response->status_line . ": " . $response->content . "\n";
		return;
	}
	my $missingdata = $json->decode($response->content);
	foreach my $row (@{$missingdata->{"rows"}}) {
		my $update = 0;
		$request = HTTP::Request->new("GET", $baseurl . $db . "/" . $row->{"value"}->{"genfrom"});
		$response = $ua->request($request);
		if($response->code != 200) {
			print "Got error " . $response->status_line . ": " . $response->content . "\n";
			next;
		}
		my $jsondoc = $json->decode($response->content);
		# we need to iterate through the doc this doc was generated from to find the id match and
		# update our title -- ick
		my $title;
		foreach my $reference (@{$jsondoc->{"docmetadata"}->{"references"}}) {
			if(exists $reference->{"acm_portal"}->{"title"}) {
				$title = $reference->{"acm_portal"}->{"title"};
				$title =~ s/, pp\. [0-9]+(?:-[0-9]+)?\.?$//;
				my $uniqid = "uniqid:" . md5_hex($title);
				if($uniqid eq $row->{"key"}) {
					$row->{"value"}->{"title"} = $title;
					$update = 1;
					last;
				}
			}
		}
		if($update) {
			$request = HTTP::Request->new("PUT", $baseurl . $db . "/" . $row->{"key"});
			$request->content(encode("utf8", $json->encode($row->{"value"})));
			$response = $ua->request($request);
			if($response->code != 201) {
				print "Got error " . $response->status_line . ": " . $response->content . "\n";
			} else {
				print "Updated " . $row->{"key"} . " with title " . $title . ".\n";
			}
		} else {
			print "Skipping " . $row->{"key"} . " (this shouldn't happen...)\n";
		}
	}
}

sub update_citations_references {
	my($server, $port, $db, $options) = @_;
	my $json = JSON->new;
	my $ua = LWP::UserAgent->new;
	$ua->cookie_jar({});
	if(exists $options->{"ssl"} && $options->{"ssl"} && exists $options->{"ssl_verify_hostname"}
		&& $options->{"ssl_verify_hostname"} == 0)
	{
		$ua->ssl_opts("verify_hostname" => 0);
	}
	my $prot = (exists $options->{"ssl"} && $options->{"ssl"}) ? "https://" : "http://";
	my $path = (exists $options->{"path"} && $options->{"path"}) ? $options->{"path"} : "/";
	my $baseurl = $prot . $server . ":" . $port . $path;
	if(exists $options->{"username"} && $options->{"username"}
		&& exists $options->{"password"} && $options->{"password"})
	{
		# we need to modify baseurl to include name/password
		$baseurl = $prot . $options->{"username"} . ":" . $options->{"password"} . "@"
			. $server . ":" . $port . $path;
	}
	# grab the list of all documents in the db
	my $request = HTTP::Request->new("GET", $baseurl . $db . "/_design/missingdata/_view/all");
	my $response = $ua->request($request);
	if($response->code != 200) {
		print "Got error " . $response->status_line . ": " . $response->content . "\n";
		return;
	}
	my $missingdata = $json->decode($response->content);
	foreach my $row (@{$missingdata->{"rows"}}) {
		my $update = 0;
		$request = HTTP::Request->new("GET", $baseurl . $db . "/" . $row->{"key"});
		$response = $ua->request($request);
		if($response->code != 200) {
			print "Got error " . $response->status_line . ": " . $response->content . "\n";
			next;
		}
		my $jsondoc = $json->decode($response->content);
		if($row->{"value"}->{"citations"} == 0 && exists $jsondoc->{"docmetadata"}->{"citations"}) {
			foreach my $citation (@{$jsondoc->{"docmetadata"}->{"citations"}}) {
				if($citation->{"acm_portal"}->{"location"} =~ m/\?id=([0-9]+)&/) {
					push(@{$jsondoc->{"citations"}}, "org.acm:$1");
					$update = 1;
				}
			}
		}
		if($row->{"value"}->{"references"} == 0 && exists $jsondoc->{"docmetadata"}->{"references"}) {
			# References not guaranteed to have a location id, in that case insert a new doc
			# (or update the existing one) with a unique generated id based on title
			foreach my $reference (@{$jsondoc->{"docmetadata"}->{"references"}}) {
				if(exists $reference->{"acm_portal"}->{"location"} &&
					$reference->{"acm_portal"}->{"location"} =~ m/\?id=([0-9]+)&/)
				{
					push(@{$jsondoc->{"references"}}, "org.acm:$1");
					$update = 1;
				} else {
					# References without locations have author info in the title and end with pp. 123-582
					# Strip out the pages but keep the author info as-is (eventually reorder or something?)
					if(!exists $reference->{"acm_portal"}->{"title"}) {
						next; # we got nothing to go on in this case, so ignore the reference
					}
					my $title = $reference->{"acm_portal"}->{"title"};
					$title =~ s/, pp\. [0-9]+(?:-[0-9]+)?\.?$//;
					my $uniqid = "uniqid:" . md5_hex($title); #Unlikely to result in collision, so should be unique
					my $newdoc = {source => "acm", _id => $uniqid, title => $title, citations => [$row->{"key"}], references => [], genfrom => $row->{"key"}};
					$request = HTTP::Request->new("PUT", $baseurl . $db . "/" . $uniqid);
					$request->content(encode("utf8", $json->encode($newdoc)));
					$response = $ua->request($request);
					if($response->code == 409) {
						# Already exists, if this gets hit that means this whole thing wasn't for naught, yay!
						$request = HTTP::Request->new("GET", $baseurl . $db . "/" . $uniqid);
						$response = $ua->request($request);
						$newdoc = $json->decode($response->content);
						my $found = 0;
						foreach my $c (@{$newdoc->{"citations"}}) {
							if($c eq $row->{"key"}) {
								$found = 1;
								last;
							}
						}
						if(!$found) {
							push(@{$newdoc->{"citations"}}, $row->{"key"});
							$request = HTTP::Request->new("PUT", $baseurl . $db . "/" . $uniqid);
							$request->content(encode("utf8", $json->encode($newdoc)));
							$response = $ua->request($request);
							if($response->code != 201) {
								print "Got error " . $response->status_line . ": " . $response->content . "\n";
							}
						}
					} elsif($response->code != 201) {
						print "Got error " . $response->status_line . ": " . $response->content . "\n";
					}
					push(@{$jsondoc->{"references"}}, $uniqid);
					$update = 1;
				}
			}
		}
		if($update) {
			$request = HTTP::Request->new("PUT", $baseurl . $db . "/" . $row->{"key"});
			$request->content(encode("utf8", $json->encode($jsondoc)));
			$response = $ua->request($request);
			if($response->code != 201) {
				print "Got error " . $response->status_line . ": " . $response->content . "\n";
			} else {
				print "Updated " . $row->{"key"} . " with " . ($#{$jsondoc->{"citations"}} + 1) . " citations and " . ($#{$jsondoc->{"references"}} + 1) . " references.\n";
			}
		} else {
			print "Skipping " . $row->{"key"} . "\n";
		}
	}
}
	
sub add_docs {
	#perl-ism to get the params passed to the subroutine
	my($file, $server, $port, $db, $options) = @_;
	open(my $fh, "<", $file) or die "Cannot open \"$file\": $!";
	my $json = JSON->new;
	#reads file line-by-line and adds it to the incremental json parser
	while(my $line = <$fh>) {
		$json->incr_parse($line);
	}
	my $documents = $json->incr_parse;
	close($fh);
	# initiate LWP stuff here
	my $ua = LWP::UserAgent->new;
	$ua->cookie_jar({});
	if(exists $options->{"ssl"} && $options->{"ssl"} && 
		exists $options->{"ssl_verify_hostname"} && $options->{"ssl_verify_hostname"} == 0)
	{
		$ua->ssl_opts("verify_hostname" => 0);
	}
	my $prot = (exists $options->{"ssl"} && $options->{"ssl"}) ? "https://" : "http://";
	my $path = (exists $options->{"path"} && $options->{"path"}) ? $options->{"path"} : "/";
	my $baseurl = $prot . $server . ":" . $port . $path;
	if(exists $options->{"username"} && $options->{"username"}
		&& exists $options->{"password"} && $options->{"password"})
	{
		# we need to modify baseurl to include name/password
		$baseurl = $prot . $options->{"username"} . ":" . $options->{"password"} . "@"
			. $server . ":" . $port . $path;
	}
	# this assumes that $documents is a valid arrayref and that incr_parse didn't barf above
	# should be fine for current input, but error checking might be nice if we start having
	# odd documents being generated. $doc should be a hashref in all instances.
	foreach my $doc (@$documents) {
		# add generated fields that are nice to have in the db but don't exist in the JSON source
		# also add _id so we can guarantee we do not add duplicates
		$doc->{"source"} = "acm";
		$doc->{"_id"} = "org.acm:" . $doc->{"id"};
		# do any other mangling here (like extracting citations from docmetadata)
		# we currently don't do this for data checkpoint but will for code checkpoint
		# if the underlying java code that generates the JSON cannot fix it
		# (actually doing this in a second pass in update_citations_references)
		# now send it off to the server
		my $request = HTTP::Request->new("PUT", $baseurl . $db . "/" . $doc->{"_id"});
		$request->content(encode("utf8", $json->encode($doc)));
		my $response = $ua->request($request);
		my $update = "Inserting ";
		if($response->code == 409 && exists $options->{"update_existing"}
			&& $options->{"update_existing"})
		{
			# need to get the rev from HEAD
			$request = HTTP::Request->new("GET", $baseurl . $db . "/" . $doc->{"_id"});
			$response = $ua->request($request);
			my $jsonresult = $json->decode($response->content);
			$doc->{"_rev"} = $jsonresult->{"_rev"};
			$request = HTTP::Request->new("PUT", $baseurl . $db . "/" . $doc->{"_id"});
			$request->content(encode("utf8", $json->encode($doc)));
			$response = $ua->request($request);
			$update = "Updating ";
		}
		print $update . $doc->{"_id"} . " and got " . $response->status_line . "\n";
	}
}

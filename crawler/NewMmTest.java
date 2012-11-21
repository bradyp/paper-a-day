/**
 * 
 */
package ecologylab.semantics.metametadata.test;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.UnsupportedEncodingException;
import java.net.MalformedURLException;
import java.net.URLDecoder;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import ecologylab.appframework.SingletonApplicationEnvironment;
import ecologylab.generic.Continuation;
import ecologylab.net.ParsedURL;
import ecologylab.semantics.collecting.MetaMetadataRepositoryInit;
import ecologylab.semantics.collecting.SemanticsSessionScope;
import ecologylab.semantics.cyberneko.CybernekoWrapper;
import ecologylab.semantics.generated.library.RepositoryMetadataTranslationScope;
import ecologylab.semantics.metadata.Metadata;
import ecologylab.semantics.metadata.builtins.Document;
import ecologylab.semantics.metadata.builtins.DocumentClosure;
import ecologylab.semantics.metadata.builtins.declarations.InformationCompositionDeclaration;
import ecologylab.serialization.SIMPLTranslationException;
import ecologylab.serialization.SimplTypesScope;
import ecologylab.serialization.SimplTypesScope.GRAPH_SWITCH;
import ecologylab.serialization.formatenums.Format;

/**
 * Basic program for testing meta-metadata. Takes a set of locations as arguments as input. (Input
 * parsing is terminated by a // comment symbol).
 * 
 * Uses semantics to download and parse each input. Sends output to the console as JSON.
 * 
 * Also construct an information_composition_declaration object. Add each metadata that gets constructed / extracted into it.
 * Write this file to the temp directory (Java's idea of where you can write).
 * Report this file's path on the console, so you can paste into Chrome and browse it.
 * 
 * @author andruid
 */
public class NewMmTest extends SingletonApplicationEnvironment implements
		Continuation<DocumentClosure>
{
	ArrayList<DocumentClosure>			documentCollection	= new ArrayList<DocumentClosure>();

	int															currentResult;
	
	static File[] listOfFiles;

	protected boolean								outputOneAtATime;

	OutputStream										outputStream;

	protected SemanticsSessionScope	semanticsSessionScope;
	
	protected InformationCompositionDeclaration informationComposition = new InformationCompositionDeclaration();

	public NewMmTest(String appName) throws SIMPLTranslationException
	{
		this(appName, System.out);
	}

	public NewMmTest(String appName, OutputStream outputStream) throws SIMPLTranslationException
	{
		this(appName, outputStream, RepositoryMetadataTranslationScope.get());
	}

	public NewMmTest(String appName, OutputStream outputStream,
			SimplTypesScope metadataTranslationScope) throws SIMPLTranslationException
	{
		this(appName, outputStream, metadataTranslationScope, null,
				MetaMetadataRepositoryInit.DEFAULT_REPOSITORY_FORMAT);
	}

	public NewMmTest(String appName, File repositoryLocation, Format repositoryFormat)
			throws SIMPLTranslationException
	{
		this(appName, System.out, repositoryLocation, repositoryFormat);
	}

	public NewMmTest(String appName, OutputStream outputStream, File repositoryLocation,
			Format repositoryFormat) throws SIMPLTranslationException
	{
		this(appName, outputStream, RepositoryMetadataTranslationScope.get(), repositoryLocation,
				repositoryFormat);
	}

	public NewMmTest(String appName, OutputStream outputStream,
			SimplTypesScope metadataTranslationScope, File repositoryLocation, Format repositoryFormat)
			throws SIMPLTranslationException
	{
		super(appName);
		SimplTypesScope.graphSwitch = GRAPH_SWITCH.ON;
		this.outputStream = outputStream;
		semanticsSessionScope = new SemanticsSessionScope(repositoryLocation, repositoryFormat,
				metadataTranslationScope, CybernekoWrapper.class);
	}

	public void collect(String[] urlStrings, String[] localStrings)
	{
		// seed start urls
		for (int i = 0; i < urlStrings.length; i++)
		{
			if ("//".equals(urlStrings[i]))
			{
				System.err.println("Terminate due to //");
				break;
			}
			if (urlStrings[i].startsWith("//"))
				continue; // commented out urls

			ParsedURL thatPurl = ParsedURL.getAbsolute(urlStrings[i]);
			
			Document document = semanticsSessionScope.getOrConstructDocument(thatPurl);

			
			if (localStrings != null)
			{
				ParsedURL localPurl = ParsedURL.getAbsolute(localStrings[i]);
				document.setLocalLocation(localPurl);
			}
			
			DocumentClosure documentClosure = document.getOrConstructClosure();
			System.out.println(documentClosure.getDownloadLocation());
			
			if (documentClosure != null) // super defensive -- make sure its not malformed or null or
																		// otherwise a mess
				documentCollection.add(documentClosure);
		}
		
		
		// process documents after parsing command line so we now how many are really coming
		for (DocumentClosure documentClosure : documentCollection)
		{
			documentClosure.addContinuation(this);
			documentClosure.queueDownload();
		}
		semanticsSessionScope.getDownloadMonitors().requestStops();
	}

	public void collect(String[] urlStrings)
	{
		// seed start urls
		for (int i = 0; i < urlStrings.length; i++)
		{
			if ("//".equals(urlStrings[i]))
			{
				System.err.println("Terminate due to //");
				break;
			}
			if (urlStrings[i].startsWith("//"))
				continue; // commented out urls

			ParsedURL thatPurl = ParsedURL.getAbsolute(urlStrings[i]);
			
			Document document = semanticsSessionScope.getOrConstructDocument(thatPurl);
			
			DocumentClosure documentClosure = document.getOrConstructClosure();
			
			if (documentClosure != null) // super defensive -- make sure its not malformed or null or
																		// otherwise a mess
				documentCollection.add(documentClosure);
		}
		
		
		// process documents after parsing command line so we now how many are really coming
		for (DocumentClosure documentClosure : documentCollection)
		{
			documentClosure.addContinuation(this);
			documentClosure.queueDownload();
		}
		semanticsSessionScope.getDownloadMonitors().requestStops();
	}
	
	public static void main(String[] args)
	{
		NewMmTest mmTest;
		try
		{
			if (args.length != 2)
			{
				StackTraceElement[] stack = Thread.currentThread ().getStackTrace ();
			    StackTraceElement main = stack[stack.length - 1];
			    String mainClass = main.getClassName ();
				
				System.out.println("Usage is:\n" + mainClass +" <input directory> <output directory>");
				return;
			}
			
			// Directory path here
			File file = new File(args[0]);
			DIR_NAME = args[1];
			String path = file.getAbsolutePath();
			System.out.println(path);
		 
			File folder = new File(path);
			listOfFiles = folder.listFiles();
			
			
			mmTest = new NewMmTest("NewMmTest");
			
			for (int i = 0; i < listOfFiles.length; i++) 
			{
			   if (listOfFiles[i].isFile()) 
			   {
				   String files = listOfFiles[i].getName();
				   String original = "http://dl.acm.org/citation.cfm?id=" + files.substring(0, files.length() -".html".length());
				   File selectorFooling = new File(path, files);
				   String local = selectorFooling.toURL().toString();	//deprecated, but fiddling with URIs is for later
				   String[] urlAccum = {original};
				   String[] localAccum = {local};
				
				   
				   mmTest.collect(urlAccum, localAccum);
			   }
			}
		}
		catch (SIMPLTranslationException e)
		{
			e.printStackTrace();
		}catch (MalformedURLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	@Override
	public synchronized void callback(DocumentClosure incomingClosure)
	{
		if (outputOneAtATime)
			output(incomingClosure);
		if (++currentResult == documentCollection.size())
		{
			if (!outputOneAtATime)
			{
				System.out.println("\n\n");
				for (DocumentClosure documentClosure : documentCollection)
					output(documentClosure);
				writeCompositionFile();
			}
			semanticsSessionScope.getDownloadMonitors().stop(false);
			
			
			try
			{
				//JSON file written, now to modify
				JSONParser parser = new JSONParser();
				Object obj = parser.parse(new FileReader(DIR_NAME + "\\" + OUT_NAME));
				 
				JSONObject jsonObject = (JSONObject) obj;
				
				JSONArray docAccum = new JSONArray();
		 
				JSONObject infocompdec = (JSONObject) jsonObject.get("information_composition_declaration");
				JSONArray metadata = (JSONArray) infocompdec.get("metadata");
				Iterator<JSONObject> iterator = metadata.iterator();
				//For each doc in the collection
				while (iterator.hasNext()) {
					
					//get location, title, abstract, citations, keywords, classifications, references
					
					JSONObject docWrite = new JSONObject();
					
					//the easy ones (loc, title, abstract, docid)
					JSONObject doc = iterator.next();
					JSONObject acm = (JSONObject) doc.get("acm_portal");
					String loc = (String) acm.get("location");
					int docid = -1;
					if (loc != null)
						docid = Integer.parseInt(loc.replaceAll("\\D", ""));
					String title = (String) acm.get("title");
					String abstrat = (String) acm.get("abstract");
					
					//citations
					JSONArray citations = (JSONArray) acm.get("citations");
					JSONArray citationsWrite = new JSONArray();
					if (citations != null)
					{
						Iterator<JSONObject> iterCite = citations.iterator();
						
						while (iterCite.hasNext()) {
							
							JSONObject citer = iterCite.next();
							JSONObject acmCite = (JSONObject) citer.get("acm_portal");
							String locCite = (String) acmCite.get("location");
							if (locCite != null)
							{
								locCite = locCite.substring(locCite.indexOf("?id=") + 4);
								locCite = locCite.substring(0, locCite.indexOf("&"));
								int docidCite = Integer.parseInt(locCite);
								citationsWrite.add(docidCite);
							}
						}
					}
					
					//references
					JSONArray references = (JSONArray) acm.get("references");
					JSONArray referencesWrite = new JSONArray();
					if (references != null)
					{
						Iterator<JSONObject> iterRef = references.iterator();
						
						while (iterRef.hasNext()) {
							JSONObject refer = iterRef.next();
							JSONObject acmRef = (JSONObject) refer.get("acm_portal");
							String locRef = (String) acmRef.get("location");
							if (locRef != null)
							{
								locRef = locRef.substring(locRef.indexOf("?id=") + 4);
								locRef = locRef.substring(0, locRef.indexOf("&"));
								int docidRef = Integer.parseInt(locRef);
								referencesWrite.add(docidRef);
							}
						}
					}
					
					//keywords
					JSONObject keywords = (JSONObject) acm.get("keywords");
					if (keywords != null)
					{
						JSONArray docu = (JSONArray) keywords.get("document");
						JSONArray keywordsWrite = new JSONArray();
						
						if (docu != null)
						{
							Iterator<JSONObject> iterKey = docu.iterator();
							
							while (iterKey.hasNext()) {
								JSONObject keyword = iterKey.next();
								String currentKey =  (String) keyword.get("title");
								
								keywordsWrite.add(currentKey);
							}
						}
						docWrite.put("keywords", keywordsWrite);
					}
					//classifications
					JSONObject classi = (JSONObject) acm.get("classification");
					if (keywords != null)
					{
						JSONArray docu = (JSONArray) keywords.get("document");
						JSONArray classiWrite = new JSONArray();
						
						if (docu != null)
						{
							Iterator<JSONObject> iterClass = docu.iterator();
							
							while (iterClass.hasNext()) {
								JSONObject classification = iterClass.next();
								String currentClass =  (String) classification.get("title");
								
								classiWrite.add(currentClass);
							}
						}
						docWrite.put("classification", classiWrite);
					}
					
					//vars per doc: docid, title, abstrat, referencesWrite, citationsWrite, keywordsWrite, classiWrite
					
					docWrite.put("id", docid);
					docWrite.put("title", title);
					docWrite.put("abstract", abstrat);
					docWrite.put("references", referencesWrite);
					docWrite.put("citations", citationsWrite);
 					docWrite.put("docmetadata", acm);		//NOT the whole lump of metadata- just for this doc
					
					docAccum.add(docWrite);
				}
				
				//write docAccum to file
				try {
					 int count = 0;
					File filetest = new File(DIR_NAME + "\\" + "out"+count+".json");
					while(filetest.exists())
					{
						count++;
						filetest = new File(DIR_NAME + "\\" + "out"+count+".json");
					}
					
					FileWriter file = new FileWriter(DIR_NAME + "\\" + "out"+count+".json");
					
					file.write(docAccum.toJSONString());
					file.flush();
					file.close();
					
					System.out.println("Wrote to: out" + count+".json");
					
				} catch (IOException e) {
					e.printStackTrace();
				} catch (Exception e)
				{
					e.printStackTrace();
				}
			}catch (FileNotFoundException e) {
				e.printStackTrace();
			} catch (IOException e) {
				e.printStackTrace();
			} catch (ParseException e) {
				e.printStackTrace();
			}
			
		}
		
	}

	private static final String OUT_PREFIX		= "mmTest";
	private static final String OUT_SUFFIX		= ".json";
	private static String DIR_NAME = "";
	private static final String OUT_NAME			= OUT_PREFIX + OUT_SUFFIX;
	
	private void writeCompositionFile()
	{
		try
		{
			File tempFile	= File.createTempFile(OUT_PREFIX, OUT_SUFFIX);
			File outFile	= new File(DIR_NAME, OUT_NAME);
			tempFile.renameTo(outFile);
			
			SimplTypesScope.serialize(informationComposition, outFile, Format.JSON);
			System.out.println("Intermediate file in: " + outFile.getAbsolutePath());
		}
		catch (Exception e)
		{
			e.printStackTrace();
		}
		
		
	}

	protected void output(DocumentClosure incomingClosure)
	{
		incomingClosure.serialize(outputStream);
		Document document	= incomingClosure.getDocument();
		if (document != null)
		{
			List<Metadata>	allMetadata	= informationComposition.getMetadata();
			if (allMetadata == null)
			{
				allMetadata	= new ArrayList<Metadata>();
				informationComposition.setMetadata(allMetadata);
			}
			allMetadata.add(document);
		}
	}
}

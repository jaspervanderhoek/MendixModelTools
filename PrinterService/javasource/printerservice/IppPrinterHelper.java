package printerservice;

import java.io.FileInputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

import javax.print.Doc;
import javax.print.DocFlavor;
import javax.print.DocPrintJob;
import javax.print.PrintService;
import javax.print.PrintServiceLookup;
import javax.print.SimpleDoc;
import javax.print.attribute.Attribute;
import javax.print.attribute.HashPrintRequestAttributeSet;
import javax.print.attribute.PrintRequestAttributeSet;
import javax.print.attribute.standard.Chromaticity;
import javax.print.attribute.standard.MediaPrintableArea;
import javax.print.attribute.standard.MediaSizeName;
import javax.print.attribute.standard.Sides;
import javax.print.event.PrintJobAdapter;
import javax.print.event.PrintJobEvent;

import com.mendix.core.Core;
import com.mendix.logging.ILogNode;
import com.mendix.systemwideinterfaces.core.IContext;
import com.mendix.systemwideinterfaces.core.IMendixObject;

import printerservice.proxies.AvailablePrinter;
import printerservice.proxies.PrintJob;
import system.proxies.FileDocument;

public class IppPrinterHelper {

	private static ILogNode _logNode;
	static {
		try {
			_logNode = Core.getLogger("PrintHelper");
		}
		catch (Exception e) {
		}
	};

	public static PrintService[] getAvailablePrintServices() {
		DocFlavor flavor = DocFlavor.SERVICE_FORMATTED.PAGEABLE;
		PrintRequestAttributeSet patts = new HashPrintRequestAttributeSet();
		patts.add(Sides.DUPLEX);

		PrintService[] ps = PrintServiceLookup.lookupPrintServices(flavor, patts);
		if ( ps.length == 0 ) {
			throw new IllegalStateException("No Printer found");
		}
		return ps;
	}

	public static List<IMendixObject> getAvailablePrintServicesAsMxObj( IContext context ) {
		List<IMendixObject> result = new ArrayList<>();

		for( PrintService printService : getAvailablePrintServices() ) {
			String docFlavors = "";
			for( DocFlavor df : printService.getSupportedDocFlavors() )
				docFlavors += df.toString() + "\r\n";

			String attributes = "";
			for( Attribute attr : printService.getAttributes().toArray() )
				attributes += attr.getCategory().getSimpleName() + "=" + attr.getName() + "\r\n";

			IMendixObject printer = Core.instantiate(context, AvailablePrinter.entityName);
			printer.setValue(context, AvailablePrinter.MemberNames.Name.toString(), printService.getName());
			printer.setValue(context, AvailablePrinter.MemberNames.SupportedDocuments.toString(), docFlavors);
			printer.setValue(context, AvailablePrinter.MemberNames.Properties.toString(), attributes);

			result.add(printer);
		}

		return result;
	}

	public static String listPrintServices( PrintService[] printServiceList ) {
		String psList = "";

		for( PrintService printService : printServiceList ) {
			String docFlavors = "";
			for( DocFlavor df : printService.getSupportedDocFlavors() )
				docFlavors += df.toString() + "\r\n";

			String attributes = "";
			for( Attribute attr : printService.getAttributes().toArray() )
				attributes += attr.getCategory().getSimpleName() + "=" + attr.getName() + "\r\n";

			psList += "\r\n________________________________\r\nPrinter \r\n";
			psList += printService.getName() + "  -  " + printService.getClass().getSimpleName() + "\r\n" + docFlavors + "\r\n" + attributes;
		}

		return psList;
	}

	public static PrintService getPrintServices( String serviceName ) {
		for( PrintService printService : getAvailablePrintServices() ) {
			if ( printService.getName().equals(serviceName) )
				return printService;
		}

		return null;
	}

	public static PrintJobWatcher printDocument( PrintService service, String location ) throws Exception {
		FileInputStream fis = new FileInputStream(location);
		return printDocument(service, fis);
	}

	public static PrintJobWatcher printDocument( PrintService service, InputStream fis ) throws Exception {
		Doc pdfDoc = new SimpleDoc(fis, DocFlavor.INPUT_STREAM.AUTOSENSE, null);
		DocPrintJob printJob = service.createPrintJob();
		HashPrintRequestAttributeSet requestAttr = new HashPrintRequestAttributeSet();

		requestAttr.add(Chromaticity.MONOCHROME);
		requestAttr.add(javax.print.attribute.standard.Sides.ONE_SIDED);
		requestAttr.add(new javax.print.attribute.standard.Copies(1));
		requestAttr.add(MediaSizeName.NA_LETTER);
		requestAttr.add(new MediaPrintableArea(0.05f, 0.05f, 0.05f, 0.05f, MediaPrintableArea.INCH));
		requestAttr.add(new javax.print.attribute.standard.PageRanges(1));


		String attributes = "";
		for( Attribute attr : printJob.getAttributes().toArray() )
			attributes += attr.getCategory().getSimpleName() + "=" + attr.getName() + "\r\n";

		// System.out.println( attributes );
		_logNode.info(attributes);
		long jobNr = System.currentTimeMillis();
		PrintJobWatcher pjw = new PrintJobWatcher(printJob, jobNr);

		printJob.print(pdfDoc, requestAttr);
		fis.close();

		return pjw;
	}

	public static PrintJobWatcher printDocument( PrintService service, IContext context, PrintJob job ) throws Exception {

		FileDocument fdoc = job.getPrintJob_FileDocument(context);

		InputStream stream = Core.getFileDocumentContent(context, fdoc.getMendixObject());

		Doc pdfDoc = new SimpleDoc(stream, DocFlavor.INPUT_STREAM.AUTOSENSE, null);
		DocPrintJob printJob = service.createPrintJob();
		HashPrintRequestAttributeSet requestAttr = new HashPrintRequestAttributeSet();

		// requestAttr.add(Chromaticity.MONOCHROME );

		requestAttr.add(javax.print.attribute.standard.Sides.ONE_SIDED);
		requestAttr.add(new javax.print.attribute.standard.Copies(job.getNrOfCopies()));

		switch (job.getPageType()) {
		case A4:
			requestAttr.add(MediaSizeName.ISO_A4);
			break;
		case NA_Letter:
			requestAttr.add(MediaSizeName.NA_LETTER);
			break;
		}

		requestAttr.add(new MediaPrintableArea(job.getMargin_x_Coordinate().floatValue(), job.getMargin_y_Coordinate().floatValue(), job
				.getMargin_width().floatValue(), job.getMargin_Height().floatValue(), MediaPrintableArea.INCH));
		requestAttr.add(new javax.print.attribute.standard.PageRanges(job.getPageRange()));


		String attributes = "";
		for( Attribute attr : printJob.getAttributes().toArray() )
			attributes += attr.getCategory().getSimpleName() + "=" + attr.getName() + "\r\n";

		// System.out.println( attributes );
		_logNode.info(attributes);
		long jobNr = job.getMendixObject().getId().toLong();
		PrintJobWatcher pjw = new PrintJobWatcher(printJob, jobNr);

		_logNode.info("Starting printjob: " + jobNr);
		printJob.print(pdfDoc, requestAttr);
		stream.close();

		return pjw;
	}

	public static class PrintJobWatcher {

		boolean done = false;
		long jobNr = 0;

		PrintJobWatcher( DocPrintJob job, long jobNr ) {
			this.jobNr = jobNr;
			job.addPrintJobListener(new PrintJobAdapter() {

				public void printJobCanceled( PrintJobEvent pje ) {
					allDone();
				}

				public void printJobCompleted( PrintJobEvent pje ) {
					allDone();
				}

				public void printJobFailed( PrintJobEvent pje ) {
					allDone();
				}

				public void printJobNoMoreEvents( PrintJobEvent pje ) {
					allDone();
				}

				void allDone() {
					synchronized (PrintJobWatcher.this) {
						done = true;
						_logNode.info("Printing done for job: " + PrintJobWatcher.this.jobNr);
						System.out.println("Printing done ...");
						PrintJobWatcher.this.notify();
					}
				}
			});
		}

		public synchronized void waitForDone() {
			try {
				while( !done ) {
					wait();
				}
			}
			catch( InterruptedException e ) {
			}
		}
	}


	public static void main( String args[] ) throws Exception {
		PrintService[] psList = getAvailablePrintServices();

		System.out.println(listPrintServices(psList));
		
//		CupsClient cp = new CupsClient();
//		CupsPrinter printer = cp.getPrinter( new URL( "http://MUS-DC1/US-PRN-01" ));
//	    List<CupsPrinter> printers = null;
//	    
//	      try {
//	        String hostname = "your host";
//	        int port = 631;
//	   
//	        CupsClient cupsClient = new CupsClient(hostname, port);
//	        printers = cupsClient.getPrinters();
//	        for (CupsPrinter p : printers) {
//	           System.out.println(p.toString());
//	        }
//	      } catch (Exception e) {
//	        e.printStackTrace();
//	      }		
		
		
//		IppPrintServiceLookup lookup = new IppPrintServiceLookup(new URI("ipp://MUS-DC1/US-PRN-01"), "mendixdomain/jvh", "wdp4ep5y!");
//		PrintService[] ps = lookup.getPrintServices();
		

//		java.awt.Desktop.getDesktop().print(new File("c:/Mendix/Temp/test.docx"));

		// printDocument(ps, "c:/Mendix/Temp/test.pdf");

//		System.out.println(ps);
	}
}

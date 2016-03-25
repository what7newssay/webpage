package mapGenerator;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;



public class Main {

	public static StringBuilder sb;
	public static BufferedReader br;
	public static BufferedWriter bw;
	public static void main(String[] args) throws IOException {
		// TODO Auto-generated method stub
		System.out.println("System Start!");
		br = new BufferedReader(new FileReader("map.html"));

		try {
			sb = new StringBuilder();
			String line = br.readLine();

			while (line != null) {
				sb.append(line);
				sb.append(System.lineSeparator());
				if(line.contains("//!!!MarkerGenLineStart"))
				{
					System.out.println("Writing Marker...");
					generateMapHtml();
				} 
				line = br.readLine();
			}
			String everything = sb.toString();
			bw = new BufferedWriter(new FileWriter("Map_gen.html"));
			bw.write(everything);
			bw.close();
		} finally {
			br.close();
		}

	}

	private static void generateMapHtml() {
		if(markerFileCheck()){
			BufferedReader mbr;
			int makerCount =1;
			try {
				mbr = new BufferedReader(new FileReader("marker.txt"));
				String mline = mbr.readLine();
				sb.append("\tvar markList = [");
				sb.append(System.lineSeparator());
				while(mline != null)
				{
					String country = mbr.readLine();
					System.out.println("Marker country is: "+country);
					String lat = mbr.readLine();
					String lng = mbr.readLine();
					sb.append("\t\t["+lat+", "+lng+", ");
					sb.append(mbr.readLine()+", '"+mbr.readLine()+"\\n\\n");
					sb.append(mbr.readLine()+"'],");
					sb.append(System.lineSeparator());
					mline = mbr.readLine();
					if(mline.contains("EndingLine"))
					{
						sb.append("\t];");
						sb.append(System.lineSeparator());
						break;
					}
					//mbr.readLine();
					
					makerCount++;
				}
				mbr.close();
			} catch (FileNotFoundException e) {
				// TODO Auto-generated catch block
				System.out.println("No marker file founded! Exit now!");
			} catch (IOException e) {
				System.out.println("File writing error! Exit now!");
			}
			//return true;
		}
		else
		{
			System.out.println("Marker file error occured.. Exited!");
		}
	}
	
	private static boolean markerFileCheck(){
		try {
			BufferedReader mbr = new BufferedReader(new FileReader("marker.txt"));
			String line = mbr.readLine();
			if(line == null)
			{
				return false;
			}
			else
			{
				if(!line.contains("StartingLine"))
					return false;
				while(line != null)
				{
					mbr.readLine();
					mbr.readLine();
					mbr.readLine();
					mbr.readLine();
					System.out.println(mbr.readLine());
					mbr.readLine();
					line=mbr.readLine();
					if(line.contains("EndingLine"))
						break;
				}
			}
			
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			System.out.println("Marker file not found!");
			return false;
		}
		catch (IOException e) {
			System.out.println("Reading maker file error! Exit now!");
			return false;
		}
		return true;
	}
}

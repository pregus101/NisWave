package com.pregus101;
import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;

public class FileAndDir {
    public static void main(String[] args) {
        System.out.println(getFiles(System.getProperty("user.home")));
        System.out.println(getDirs(System.getProperty("user.home")));
    }

    public static ArrayList<Path> getFiles(String dir){
        Path dirPath = Paths.get(dir);
        try (Stream<Path> stream = Files.list(dirPath)){
            Map<Boolean, List<Path>> partitioned = stream.collect(
                Collectors.partitioningBy(Files::isDirectory)
            );
            ArrayList<Path> out = new ArrayList<Path>(partitioned.get(false));

            for (int i = 0; i < out.size();) {
                    if (!out.get(i).toString().substring(out.get(i).toString().length()-4, out.get(i).toString().length()).equals(".mp3") || out.get(i).toString().substring(0, 1).equals(".")) {
                    out.remove(out.get(i));
                }
                else {
                    i++;
                }
            }
            return out;
        }
        catch (IOException e) {
            e.printStackTrace();
            return new ArrayList<Path>();
        }
    }

    public static ArrayList<Path> getDirs(String dir){
        Path dirPath = Paths.get(dir);
        try (Stream<Path> stream = Files.list(dirPath)){
            Map<Boolean, List<Path>> partitioned = stream.collect(
                Collectors.partitioningBy(Files::isDirectory)
            );
            return new ArrayList<Path>(partitioned.get(true));
        } 
        catch (IOException e) {
                e.printStackTrace();
                return new ArrayList<Path>();
            }
        
    }

    public static ArrayList<Path> getFiles(Path dirPath){
        try (Stream<Path> stream = Files.list(dirPath)){
            Map<Boolean, List<Path>> partitioned = stream.collect(
                Collectors.partitioningBy(Files::isDirectory)
            );

            ArrayList<Path> out = new ArrayList<Path>(partitioned.get(false));

            for (int i = 0; i < out.size();) {
                if (!out.get(i).toString().substring(out.get(i).toString().length()-4, out.get(i).toString().length()).equals(".mp3") || out.get(i).toString().substring(dirPath.toString().length()+1, dirPath.toString().length()+2).equals(".")) {
                    out.remove(out.get(i));
                }
                else {
                    i++;
                }
            }
            return out;
        }
        catch (IOException e) {
            e.printStackTrace();
            return new ArrayList<Path>();
        }
    }

    public static ArrayList<Path> getDirs(Path dirPath){
        try (Stream<Path> stream = Files.list(dirPath)){
            Map<Boolean, List<Path>> partitioned = stream.collect(
                Collectors.partitioningBy(Files::isDirectory)
            );
            return new ArrayList<Path>(partitioned.get(true));
        } 
        catch (IOException e) {
                e.printStackTrace();
                return new ArrayList<Path>();
            }
        
    }
}

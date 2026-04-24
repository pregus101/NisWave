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
            return new ArrayList<Path>(partitioned.get(false));
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
            return new ArrayList<Path>(partitioned.get(false));
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

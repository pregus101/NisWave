import java.io.IOException;
import java.lang.reflect.Array;
import java.nio.file;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.stream.Stream;

public class FileAndDir {
    public static void main(String[] args) {
        getFiles(System.getProperty("user.home"));
        getDirs(System.getProperty("user.home"));
    }

    public static ArrayList<Path> getFiles(String dir){
        ArrayList<Path> files = new ArrayList<Path>();
        return files;
    }

    public static ArrayList<Path> getDirs(String dir){
        ArrayList<Path> dirs = new ArrayList<Path>();
        return dirs;
    }
}

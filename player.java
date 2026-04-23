
import java.nio.file.Path;
import java.util.ArrayList;

public class player {
    public String playing_song = "";
    public Path current_dir;
    private ArrayList<Path> unshuffled;
    public ArrayList<Path> queue;
    private boolean shuffled = false;
    public player(Path current_dir){
        this.current_dir = current_dir;
        unshuffled = FileAndDir.getFiles(current_dir);
    }
}

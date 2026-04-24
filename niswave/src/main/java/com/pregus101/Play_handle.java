package com.pregus101;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.io.FileInputStream;
import javazoom.jl.player.Player;

public class Play_handle {
    public String playing_song = "";
    public Path current_dir;
    private ArrayList<Path> unshuffled;
    public ArrayList<Path> queue;
    private boolean shuffled = false;
    private int index = 0;
    private boolean playing = false;
    private Player player;
    
    public Play_handle(Path current_dir){
        this.current_dir = current_dir;
        unshuffled = FileAndDir.getFiles(current_dir);
    }

    public void play(Path songPath){
        index = 0;
        queue = new ArrayList<Path>(unshuffled);
        if (shuffled) {
            Collections.shuffle(queue);
            queue.remove(songPath);
            queue.add(0, songPath);
        }
        else {
            index = unshuffled.indexOf(songPath);
        }
        loadSong(songPath);
    }

    public void skip(){
        index++;
        loadSong(queue.get(index));
    }

    public void previous(){
        index--;
        loadSong(queue.get(index));
    }

    public void shuffle(){

    }

    public void pause(){
        
    }

    private void loadSong(Path songPath){
        try {
            FileInputStream fileInputStream = new FileInputStream(songPath.toString());
            player = new Player(fileInputStream);
            System.out.println("Playing...");
            player.play();
        } catch (Exception e) {
            System.out.println(e);
        }
    }
}

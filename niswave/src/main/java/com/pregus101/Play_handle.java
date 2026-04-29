package com.pregus101;
import java.nio.file.FileSystems;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.io.FileInputStream;
import javazoom.jl.player.Player;

class MyRunnable implements Runnable {
    public void run() {
        System.out.println("Thread is running via Runnable");
    }
}

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
        
        if (!queue.isEmpty()) {
            loadSong(queue.get(index));
        }
    }

    public void play(){
        index = 0;
        queue = new ArrayList<Path>(unshuffled);

        if (shuffled) {
            Collections.shuffle(queue);
        }

        if (!queue.isEmpty()) {
            loadSong(queue.get(index));
        }
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
        shuffled = !shuffled;
    }

    public void pause(){
        
    }

    public void updatePath(Path updatedPath){
        current_dir = updatedPath;
    }

    private void loadSong(Path songPath){
        if (player != null){
            player.close();
        }
        new Thread(() -> {
            try {
                FileInputStream fileInputStream = new FileInputStream(songPath.toString());
                player = new Player(fileInputStream);
                System.out.println("Playing...");
                player.play();
            } catch (Exception e) {
                System.out.println(e);
            }
        }).start();
    }
}

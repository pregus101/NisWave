package com.pregus101;
import java.nio.file.FileSystems;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.io.FileInputStream;

import javazoom.jlgui.basicplayer.*;;

class MyRunnable implements Runnable {
    public void run() {
        System.out.println("Thread is running via Runnable");
    }
}

public class Play_handle {
    public String playing_song = "";
    public Path playing_song_path;
    public Path current_dir;
    private ArrayList<Path> unshuffled;
    public ArrayList<Path> queue;
    public boolean shuffled = false;
    private int index = 0;
    private boolean playing = false;
    private boolean paused = true;
    private BasicPlayer player;
    private double pausePos;
    
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
            paused = false;
            playing = true;
        }
        else{
            paused = true;
            playing = false;
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
            paused = false;
            playing = true;
        }
        else{
            paused = true;
            playing = false;
        }
    }

    public void skip(){
        if (index < queue.size() - 1) {
            index++;
            loadSong(queue.get(index));
        }
        else {
            player.stop();
            playing = false;
        }
    }

    public void previous(){
        if (!queue.isEmpty()){
            if (index > 0) {
                index--;
            }
            loadSong(queue.get(index));
        }
    }

    public void shuffle(){
        shuffled = !shuffled;

        if (shuffled){
            Collections.shuffle(queue);
            queue.remove(playing_song_path);
            queue.add(0, playing_song_path);
        }
        else {
            queue = new ArrayList<>(unshuffled);
        }
        index = queue.indexOf(playing_song_path);
    }

    public void pause(){
        if (playing){
            if (paused){
                pausePos = player.getPosition();
                player.stop();
            }
            else{
                loadSong(queue.get(index));
                
            }
            paused = !paused;
        }
        else {
            play();
        }
    }

    public void updatePath(Path updatedPath){
        current_dir = updatedPath;
    }

    private void loadSong(Path songPath){
        playing_song = songPath.getFileName().toString();
        playing_song_path = songPath;
        if (player != null){
            player.stop();
        }
        new Thread(() -> {
            try {
                FileInputStream fileInputStream = new FileInputStream(songPath.toString());
                player = new BasicPlayer();
                System.out.println("Playing: " + playing_song.toString());
                player.play();
            } catch (Exception e) {
                System.out.println(e);
            }
        }).start();
    }
}

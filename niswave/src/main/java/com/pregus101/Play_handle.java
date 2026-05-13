package com.pregus101;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;

import javazoom.jlgui.basicplayer.*;

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
    public boolean paused = true;
    private BasicController player = (BasicController) new BasicPlayer();
    private double pausePos;
    private boolean switching = false;
    
    public Play_handle(Path current_dir){
        this.current_dir = current_dir;
        unshuffled = FileAndDir.getFiles(current_dir);
        new Thread(() -> {
            while (true) { 
                if (player != null && playing && !paused && ((BasicPlayer) player).getStatus() == BasicPlayer.STOPPED && !switching){
                    this.skip();
                }

                // try {
                //     Thread.sleep(500);
                // } catch (InterruptedException) {
                //     break;
                // }
            }
        }).start();
    }

    public void play(Path songPath){
        index = 0;
        if (!playing){
            unshuffled = FileAndDir.getFiles(current_dir);
        }
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
        if (!playing){
            unshuffled = FileAndDir.getFiles(current_dir);
        }
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
            try {
                player.stop();
            }
            catch (Exception e){
                e.printStackTrace();
            }
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
            paused = !paused;
            try {
                if (paused){
                    player.pause();
                }
                else{
                    
                    player.resume();
                }
            }
            catch (BasicPlayerException e){
                e.printStackTrace();
            }
        }
        else {
            play();
        }
    }

    public void updatePath(Path updatedPath){
        current_dir = updatedPath;
    }

    private void loadSong(Path songPath){
        switching = true;
        playing_song = songPath.getFileName().toString();
        playing_song_path = songPath;
        
        try {
            player.stop();
            player.open(songPath.toFile());
            player.play();
            paused = false;
            playing = true;
            System.out.println("Playing: " + playing_song.toString());
        }

        catch (Exception e) {
            e.printStackTrace();
        }
        switching = false;

        // if (player != null){
        // }
        // new Thread(() -> {
        //     try {
        //         FileInputStream fileInputStream = new FileInputStream(songPath.toString());
        //         player = new BasicPlayer();
        //         System.out.println("Playing: " + playing_song.toString());
        //         player.play();
        //     } catch (Exception e) {
        //         System.out.println(e);
        //     }
        // }).start();
    }
}

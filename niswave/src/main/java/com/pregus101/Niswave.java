package com.pregus101;
import java.nio.file.FileSystems;

public class Niswave {
    public static void main(String[] args){
        Play_handle player = new Play_handle(FileSystems.getDefault().getPath(System.getProperty("user.home")));
        player.play(FileSystems.getDefault().getPath("D:\\Music\\Wha\\Crystal Castles - Transgender.mp3"));
    }
}

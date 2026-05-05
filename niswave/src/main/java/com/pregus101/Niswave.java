package com.pregus101;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Graphics;
import java.io.File;
import java.nio.file.FileSystems;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JPanel;

public class Niswave extends JPanel {
    public static void main(String[] args) {
        Play_handle player = new Play_handle(FileSystems.getDefault().getPath(System.getProperty("user.home")+File.separator+"Music"+File.separator+"Breakcore For Breakfast"));
        System.out.println(FileSystems.getDefault().getPath(System.getProperty("user.home")+File.separator+"Music"+File.separator+"Breakcore For Breakfast"));
        JFrame frame = new JFrame("NisWave");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new BorderLayout());

        JPanel canvas = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                g.setColor(Color.gray);
                g.fillRect(50, 50, 100, 100);
            }
        };

        canvas.setBackground(Color.black);

        JPanel controls = new JPanel();
        JButton previousButton = new JButton("Previous");
        JButton pauseButton = new JButton("Play");
        JButton skipButton = new JButton("Skip");
        JButton shuffleButton = new JButton("Shuffle"); 

        controls.add(previousButton);
        controls.add(pauseButton);
        controls.add(skipButton);
        controls.add(shuffleButton);

        frame.add(canvas, BorderLayout.CENTER);
        frame.add(controls, BorderLayout.SOUTH);
        frame.setSize(400, 400);
        frame.setVisible(true);

        previousButton.addActionListener(e -> player.previous());
        pauseButton.addActionListener(e -> player.pause());
        // pauseButton.addActionListener(e -> playToggle(player, pauseButton));
        skipButton.addActionListener(e -> player.skip());
        shuffleButton.addActionListener(e -> player.shuffle());
        shuffleButton.addActionListener(e -> shuffleToggle(player, shuffleButton));
        
    }

    public static void shuffleToggle(Play_handle player, JButton shuffleButton){
        if (player.shuffled){
            shuffleButton.setName("shuffled");
        }
        else {
            shuffleButton.setName("shuffle");
        }
    }

    // public static void playToggle(Play_handle player, JButton pauseButton){
    //     if (player.shuffled){
    //         pauseButton.setName("pause");
    //     }
    //     else {
    //         pauseButton.setName("play");
    //     }
    // }
}


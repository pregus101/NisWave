package com.pregus101;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics;
import java.io.File;
import java.nio.file.FileSystems;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JPanel;

public class Niswave extends JPanel {
    public static void main(String[] args) {
        try {
            Play_handle player = new Play_handle(FileSystems.getDefault().getPath(System.getProperty("user.home")+File.separator+"Music"+File.separator+"Breakcore For Breakfast"));
            System.out.println(FileSystems.getDefault().getPath(System.getProperty("user.home")+File.separator+"Music"+File.separator+"Breakcore For Breakfast"));
            JFrame frame = new JFrame("NisWave");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setLayout(new BorderLayout());

            JPanel canvas = new JPanel() {
                @Override
                protected void paintComponent(Graphics g) {
                    super.paintComponent(g);
                    g.setFont(new Font("Monospaced", Font.BOLD, 16)); 
                    g.setColor(Color.GREEN);
                    if (player.playing_song != null) {
                        // Draw string at x=10, y=25
                        g.drawString("NOW PLAYING: " + player.playing_song, 10, (frame.getHeight()/4)*3);
                    }
                }
            };

            canvas.setBackground(Color.black);

            JPanel controls = new JPanel();
            controls.setBackground(new Color(143, 11, 224));
            JButton previousButton = new JButton("Previous");
            previousButton.setBackground(Color.green);
            JButton pauseButton = new JButton("Play");
            pauseButton.setBackground(Color.green);
            JButton skipButton = new JButton("Skip");
            skipButton.setBackground(Color.green);
            JButton shuffleButton = new JButton("Shuffle"); 
            shuffleButton.setBackground(Color.green);

            controls.add(previousButton);
            controls.add(pauseButton);
            controls.add(skipButton);
            controls.add(shuffleButton);

            frame.add(canvas, BorderLayout.CENTER);
            frame.add(controls, BorderLayout.SOUTH);
            frame.setSize(400, 400);
            frame.setVisible(true);

            previousButton.addActionListener(e -> {
                player.previous();
                playToggle(player, pauseButton);
                canvas.repaint();
            });
            pauseButton.addActionListener(e -> {
                player.pause();
                playToggle(player, pauseButton);
                canvas.repaint();
            });

            skipButton.addActionListener(e -> {
                player.skip();
                playToggle(player, pauseButton);
                canvas.repaint();
            });
            shuffleButton.addActionListener(e -> {
                player.shuffle();
                shuffleToggle(player, shuffleButton);
                controls.repaint();
            });
        }
        catch (Exception e){
            e.printStackTrace();
        }

    }

    public static void shuffleToggle(Play_handle player, JButton shuffleButton){
        if (player.shuffled){
            shuffleButton.setText("Shuffled");
        }
        else {
            shuffleButton.setText("Shuffle");
        }
    }

    public static void playToggle(Play_handle player, JButton pauseButton){
        if (player.paused){
            pauseButton.setText("Play");
        }
        else {
            pauseButton.setText("Pause");
        }
    }
}


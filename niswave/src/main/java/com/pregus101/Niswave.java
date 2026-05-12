package com.pregus101;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.Graphics;
import java.io.File;
import java.nio.file.FileSystems;
import java.nio.file.Path;
import java.util.ArrayList;

import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JScrollPane;

public class Niswave extends JPanel {
    public static void main(String[] args) {
        try {
            Path musicPath = FileSystems.getDefault().getPath(System.getProperty("user.home") + File.separator + "Music");
            Play_handle player = new Play_handle(musicPath);

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
                        g.drawString("NOW PLAYING: " + player.playing_song, 10, (getHeight() / 4) * 3);
                    }
                }
            };
            canvas.setBackground(Color.black);

            JPanel dirNav = new JPanel();
            dirNav.setLayout(new BoxLayout(dirNav, BoxLayout.Y_AXIS)); // Vertical Layout
            
            JScrollPane scrollPane = new JScrollPane(dirNav);
            scrollPane.setPreferredSize(new Dimension(150, 400));
            scrollPane.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED);
            scrollPane.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);

            refreshButton(dirNav, musicPath, player);

            JPanel controls = new JPanel();
            controls.setBackground(new Color(143, 11, 224));
            JButton previousButton = createStyledButton("Previous");
            JButton pauseButton = createStyledButton("Play");
            JButton skipButton = createStyledButton("Skip");
            JButton shuffleButton = createStyledButton("Shuffle");

            controls.add(previousButton);
            controls.add(pauseButton);
            controls.add(skipButton);
            controls.add(shuffleButton);

            frame.add(canvas, BorderLayout.CENTER);
            frame.add(scrollPane, BorderLayout.WEST);
            frame.add(controls, BorderLayout.SOUTH);
            
            frame.setSize(600, 500);
            frame.setLocationRelativeTo(null);
            frame.setVisible(true);

            previousButton.addActionListener(e -> { player.previous(); playToggle(player, pauseButton); canvas.repaint(); });
            pauseButton.addActionListener(e -> { player.pause(); playToggle(player, pauseButton); canvas.repaint(); });
            skipButton.addActionListener(e -> { player.skip(); playToggle(player, pauseButton); canvas.repaint(); });
            shuffleButton.addActionListener(e -> { player.shuffle(); shuffleToggle(player, shuffleButton); });

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void refreshButton(JPanel dirNav, Path dir, Play_handle player) {
        dirNav.removeAll();
        
        JButton backBtn = new JButton("...");
        backBtn.setAlignmentX(Component.LEFT_ALIGNMENT);
        backBtn.addActionListener(e -> {
            if (dir.getParent() != null) {
                player.current_dir = dir.getParent();
                refreshButton(dirNav, player.current_dir, player);
            }
        });
        dirNav.add(backBtn);
        dirNav.add(Box.createVerticalStrut(5));

        ArrayList<Path> dirs = FileAndDir.getDirs(dir);
        for (Path iDir : dirs) {
            JButton btn = new JButton(iDir.getFileName().toString());
            btn.setAlignmentX(Component.LEFT_ALIGNMENT);
            btn.setMaximumSize(new Dimension(140, 30)); 
            btn.addActionListener(e -> {
                player.current_dir = iDir;
                refreshButton(dirNav, iDir, player);
            });
            dirNav.add(btn);
            dirNav.add(Box.createVerticalStrut(5)); 
        }

        dirNav.revalidate(); 
        dirNav.repaint();    
    }

    private static JButton createStyledButton(String text) {
        JButton b = new JButton(text);
        b.setBackground(Color.green);
        return b;
    }

    public static void shuffleToggle(Play_handle player, JButton shuffleButton) {
        shuffleButton.setText(player.shuffled ? "Shuffled" : "Shuffle");
    }

    public static void playToggle(Play_handle player, JButton pauseButton) {
        pauseButton.setText(player.paused ? "Play" : "Pause");
    }
}

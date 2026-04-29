package com.pregus101;
import java.awt.BorderLayout;
import java.awt.Graphics;
import java.nio.file.FileSystems;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JPanel;

import javafx.scene.paint.Color;

public class Niswave extends JPanel {
    public static void main(String[] args) {
        Play_handle player = new Play_handle(FileSystems.getDefault().getPath("D:\\Music\\Wha"));
        JFrame frame = new JFrame("NisWave");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new BorderLayout());

        JPanel canvas = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                g.setColor(Color.MAGENTA);
                g.fillOval(50, 50, 100, 100);
            }
        };

        canvas.setBackground(Color.BLACK);

        JPanel controls = new JPanel();
        JButton redBtn = new JButton("Red");
        JButton blueBtn = new JButton("Blue");

        controls.add(redBtn);
        controls.add(blueBtn);

        frame.add(canvas, BorderLayout.CENTER);
        frame.add(controls, BorderLayout.SOUTH);
        frame.setSize(400, 400);
        frame.setVisible(true);
    

    // @Override
    // protected void paint(Graphics g) {
    //     super.paint(g);
    //     Graphics2D g2d = (Graphics2D) g;

    //     g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);


    
    //     panel.addMouseListener(new MouseAdapter() {
    //     @Override
    //     public void mousePressed(MouseEvent e) {
    //         int x = e.getX(); // Get click horizontal position
    //         int y = e.getY(); // Get click vertical position
    //         System.out.println("Mouse pressed at: " + x + "," + y);
    //     }
    // });    
    // }
    }
}


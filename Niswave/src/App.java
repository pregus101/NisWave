import java.awt.*;

public class App {
    public static void main(String[] args) throws Exception {
        Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
        int width = (int) screenSize.getWidth();
        int height = (int) screenSize.getHeight()-100;
        StdDraw.setCanvasSize(width, height);
        StdDraw.setXscale(0, width);
        StdDraw.setYscale(0, height);
        Display screen = new Display();
        while (true) {
            screen.update();
        }
    }
}

public class Display {
    private boolean needsUpdate = true;
    private int width;
    private int height;
    public void update(){
        if (needsUpdate){
            draw();
        }
        needsUpdate = false;
    }

    public Display(int width, int height) {
        this.width = width;
        this.height = height;
    }

    private void draw(){
        StdDraw.setPenColor(StdDraw.BLACK);
        StdDraw.filledRectangle((width-width/5)/2+width/5,height/2,(width-width/5)/2, height/2);
        StdDraw.setPenColor(StdDraw.GRAY);
        StdDraw.filledRectangle((width/5)/2, height/2, (width/5)/2, height/2);
    }
}

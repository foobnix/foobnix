package com.foobnix.gui;

import java.awt.event.TextEvent;

import javax.swing.GroupLayout.Alignment;

import com.trolltech.qt.core.Qt.Orientation;
import com.trolltech.qt.gui.QAction;
import com.trolltech.qt.gui.QApplication;
import com.trolltech.qt.gui.QBoxLayout;
import com.trolltech.qt.gui.QFrame;
import com.trolltech.qt.gui.QGraphicsView;
import com.trolltech.qt.gui.QHBoxLayout;
import com.trolltech.qt.gui.QIcon;
import com.trolltech.qt.gui.QImage;
import com.trolltech.qt.gui.QLabel;
import com.trolltech.qt.gui.QLineEdit;
import com.trolltech.qt.gui.QListView;
import com.trolltech.qt.gui.QMainWindow;
import com.trolltech.qt.gui.QMenu;
import com.trolltech.qt.gui.QPixmap;
import com.trolltech.qt.gui.QProgressBar;
import com.trolltech.qt.gui.QPushButton;
import com.trolltech.qt.gui.QSlider;
import com.trolltech.qt.gui.QSplitter;
import com.trolltech.qt.gui.QTabWidget;
import com.trolltech.qt.gui.QTableView;
import com.trolltech.qt.gui.QTableWidget;
import com.trolltech.qt.gui.QToolBar;
import com.trolltech.qt.gui.QVBoxLayout;
import com.trolltech.qt.gui.QWidget;
import com.trolltech.qt.gui.QImage.Format;
import com.trolltech.qt.gui.QTabWidget.TabPosition;
import com.trolltech.qt.phonon.VolumeSlider;

public class PlayerGui extends QMainWindow {

    public PlayerGui() {
        setupUI();
    }

    private void setupUI() {
   
        
        QVBoxLayout mainLayout = new QVBoxLayout();        
        QHBoxLayout topPanel = getTopPanel();
        QHBoxLayout centerLayout = new QHBoxLayout();
        
        
        QWidget rightPanel = rightPanel();
        QSplitter lefpMiddleSplitter = lefpPanel();
        
        
        
        QSplitter splitter = new QSplitter(Orientation.Horizontal);
        splitter.addWidget(lefpMiddleSplitter);
        splitter.addWidget(rightPanel);
        
        centerLayout.addWidget(splitter);
        
        
        mainLayout.addLayout(topPanel);
        mainLayout.addLayout(centerLayout);
        
        
        
        QWidget widget = new QWidget();
        widget.setLayout(mainLayout);

        setCentralWidget(widget);
        setWindowTitle("Phonon Music Player");
        setWindowIcon(new QIcon("classpath:images/foobnix-64.png"));

    }

    private QSplitter lefpPanel() {
        QWidget frame = lefpTools();
        QSplitter lefpMiddleSplitter = new QSplitter(Orientation.Vertical);
        lefpMiddleSplitter.addWidget(frame);
        QVBoxLayout box = new QVBoxLayout();
        box.addWidget(new QTableWidget(3,1));
        QWidget wi = new QWidget();
        wi.setLayout(box);
        lefpMiddleSplitter.addWidget(wi);
        return lefpMiddleSplitter;
    }

    private QWidget rightPanel() {
        QVBoxLayout right = new QVBoxLayout();
        
        
        QHBoxLayout searchLine = new QHBoxLayout();
        searchLine.addWidget(new QLineEdit("[input artis hear]"));
        searchLine.addWidget(new QPushButton("Search"));
        
        QHBoxLayout actionLine = new QHBoxLayout();
        actionLine.addWidget(new QPushButton("Top Songs"));
        actionLine.addWidget(new QPushButton("Top Albums"));
        actionLine.addWidget(new QPushButton("Top Similar"));
        actionLine.addWidget(new QPushButton("Tags"));
        actionLine.addWidget(new QPushButton("VK Search"));
        
        right.addLayout(searchLine);
        right.addLayout(actionLine);
        
        QHBoxLayout lay = new QHBoxLayout();

        QTabWidget tabs= new QTabWidget();
        tabs.setTabPosition(TabPosition.West);
        tabs.addTab(new QTableWidget(20,1), "Search");
        tabs.addTab(new QPushButton(), "Search1");
        tabs.addTab(new QPushButton(), "Search3");
        
        lay.addWidget(tabs);
        
        QVBoxLayout info = new QVBoxLayout();
        
        info.addWidget(new QLabel("<b>Album</b"));
        QPixmap image = new QPixmap("classpath:images/blank-disc.jpg");
        QLabel imageLabel = new QLabel();
        imageLabel.setPixmap(image);
        
        info.addWidget(imageLabel);
        info.addWidget(new QTableWidget(4,1));
        info.addWidget(new QLabel("<b>Album</b"));
        info.addWidget(new QTableWidget(10,1));
        
        lay.addLayout(info);
        
        right.addLayout(lay);
        
       
        
       
        QWidget frame1 = new QWidget();
        frame1.setLayout(right);
        return frame1;
    }

    private QWidget lefpTools() {
        QVBoxLayout left = new QVBoxLayout();
        left.addWidget(new QTableWidget(10,1));
        QToolBar qToolBar = new QToolBar();
        qToolBar.addAction(new QAction("Music",this));
        qToolBar.addAction(new QAction("Radio",this));
        qToolBar.addAction(new QAction("Lists",this));
        qToolBar.addAction(new QAction("Charts",this));
        left.addWidget(qToolBar);
        
        left.addWidget(new QLineEdit("filter"));
        
        
        QWidget frame = new QWidget();
        frame.setLayout(left);
        return frame;
    }

    private QHBoxLayout getTopPanel() {
        QHBoxLayout topPanel = new QHBoxLayout();
        
        topPanel.addWidget(new QPushButton("Menu"));
        topPanel.addWidget(new QPushButton("Stop"));
        topPanel.addWidget(new QPushButton("Play"));
        topPanel.addWidget(new QPushButton("Pause"));
        topPanel.addWidget(new QPushButton("Next"));
        topPanel.addWidget(new QPushButton("Prev"));
        
        topPanel.addWidget(new QSlider(Orientation.Horizontal));
        QProgressBar progressBar = new QProgressBar();
        progressBar.setMinimumWidth(200);
        progressBar.setTextVisible(true);
        progressBar.setValue(20);
        progressBar.setFormat("00:00");
        
        
        topPanel.addWidget(progressBar);
        return topPanel;
    }

    public static void main(String args[]) {
        QApplication.initialize(args);
        QApplication.setApplicationName("Music Player");

        new PlayerGui().show();

        QApplication.exec();
    }

}

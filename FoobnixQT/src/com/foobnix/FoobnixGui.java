package com.foobnix;

import com.trolltech.qt.gui.QApplication;
import com.trolltech.qt.gui.QHBoxLayout;
import com.trolltech.qt.gui.QLineEdit;
import com.trolltech.qt.gui.QPushButton;
import com.trolltech.qt.gui.QTableWidget;
import com.trolltech.qt.gui.QTableWidgetItem;
import com.trolltech.qt.gui.QVBoxLayout;
import com.trolltech.qt.gui.QWidget;
import com.trolltech.qt.phonon.AudioOutput;
import com.trolltech.qt.phonon.MediaObject;
import com.trolltech.qt.phonon.MediaSource;
import com.trolltech.qt.phonon.Phonon;

public class FoobnixGui extends QWidget {

    public static void main(String[] args) {
        QApplication.initialize(args);

        FoobnixGui gui = new FoobnixGui(null);

        QVBoxLayout layout = new QVBoxLayout(gui);

        QHBoxLayout searchLineLayout = new QHBoxLayout(null);

        QLineEdit searchLine = new QLineEdit();
        QPushButton searchButton = new QPushButton("Search");
        searchLineLayout.addWidget(searchLine);
        searchLineLayout.addWidget(searchButton);

        layout.addLayout(searchLineLayout);

        QHBoxLayout typeButtonsLayout = new QHBoxLayout(null);
        typeButtonsLayout.addWidget(new QPushButton("Top Artist"));
        typeButtonsLayout.addWidget(new QPushButton("Top Song"));
        typeButtonsLayout.addWidget(new QPushButton("Top Similar"));

        layout.addLayout(typeButtonsLayout);

        QTableWidget list = new QTableWidget(0, 4);
        int currentRow = list.rowCount();
        list.insertRow(currentRow);
        list.setItem(currentRow, 0, new QTableWidgetItem("asdf1"));
        list.setItem(currentRow, 1, new QTableWidgetItem("asdf2"));
        list.setItem(currentRow, 2, new QTableWidgetItem("asdf3"));

        layout.addWidget(list);

        AudioOutput audioOutput = new AudioOutput(Phonon.Category.MusicCategory);
        MediaObject mediaObject = new MediaObject(null);
        Phonon.createPath(mediaObject, audioOutput);

        // mediaObject.setCurrentSource(new
        // MediaSource("/home/ivan/Music/CD1/01 Another Brick In The Wall.mp3"));
        mediaObject.setCurrentSource(new MediaSource("http://cs4406.vkontakte.ru/u17609241/audio/770956469106.mp3"));
        mediaObject.play();

        gui.show();

        QApplication.exec();
    }

    public FoobnixGui(QWidget parent) {
        super(parent);
    }
}

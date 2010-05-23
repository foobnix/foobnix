package com.foobnix.gui;

import java.util.Collection;
import java.util.List;

import net.roarsoftware.lastfm.Artist;
import net.roarsoftware.lastfm.Track;

import org.apache.commons.collections.CollectionUtils;
import org.apache.commons.lang.StringUtils;

import com.foobnix.vk.VKClient;
import com.foobnix.vk.VkSong;
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

    String LAST_FM_KEY = "bca6866edc9bdcec8d5e8c32f709bea1";
    private final QTableWidget list = new QTableWidget(0, 1);
    private final QLineEdit searchLine = new QLineEdit();
    VKClient client = new VKClient("qax@bigmir.net", "foobnix");
    AudioOutput audioOutput = new AudioOutput(Phonon.Category.MusicCategory);
    MediaObject mediaObject = new MediaObject(null);

    public FoobnixGui() {
        FoobnixGui gui = new FoobnixGui(null);
        gui.setGeometry(0, 0, 500, 800);

        QVBoxLayout layout = new QVBoxLayout(gui);

        QHBoxLayout searchLineLayout = new QHBoxLayout(null);

        QPushButton searchButton = new QPushButton("Search");
        searchButton.clicked.connect(this, "search()");
        searchLineLayout.addWidget(searchLine);
        searchLineLayout.addWidget(searchButton);

        list.clicked.connect(this, "onRowClick()");

        layout.addLayout(searchLineLayout);

        QHBoxLayout typeButtonsLayout = new QHBoxLayout(null);
        typeButtonsLayout.addWidget(new QPushButton("Top Artist"));
        typeButtonsLayout.addWidget(new QPushButton("Top Song"));
        typeButtonsLayout.addWidget(new QPushButton("Top Similar"));

        layout.addLayout(typeButtonsLayout);

        layout.addWidget(list);

        Phonon.createPath(mediaObject, audioOutput);

        // mediaObject.setCurrentSource(new
        // MediaSource("http://cs4406.vkontakte.ru/u17609241/audio/770956469106.mp3"));
        mediaObject.play();

        gui.show();
    }

    public void onRowClick() {
        List<QTableWidgetItem> rows = list.selectedItems();
        if (CollectionUtils.isNotEmpty(rows)) {
            QTableWidgetItem qTableWidgetItem = rows.get(0);
            String text = qTableWidgetItem.text();
            List<VkSong> search = client.search(text);
            VkSong song = search.get(0);
            mediaObject.clearQueue();
            mediaObject.stop();
            mediaObject.setCurrentSource(new MediaSource(song.getPath()));
            mediaObject.play();

        }

    }

    public void search() {
        String text = searchLine.text();
        if (StringUtils.isEmpty(text))
            list.clear();

        Collection<Track> tracks = Artist.getTopTracks(text, LAST_FM_KEY);
        for (Track track : tracks) {
            addLine(list, track.getArtist() + " - " + track.getName());
        }

    }

    public static void main(String[] args) {
        QApplication.initialize(args);

        new FoobnixGui();
        QApplication.exec();
    }

    public void search(String query) {

    }

    private static void addLine(QTableWidget list, String value) {
        int currentRow = list.rowCount();
        list.insertRow(currentRow);
        list.setItem(currentRow, 0, new QTableWidgetItem(value));
    }

    public FoobnixGui(QWidget parent) {
        super(parent);
    }
}

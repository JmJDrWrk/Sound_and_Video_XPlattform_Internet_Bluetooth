package com.example.bluetoothinternetaudiocard

import android.content.Context
import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioManager
import android.media.AudioTrack
import android.net.wifi.WifiManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers

import kotlinx.coroutines.launch
import java.io.BufferedReader
import java.io.BufferedWriter
import java.io.IOException
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.net.Socket
import java.nio.ByteBuffer

class AudioReceiver {

    private lateinit var socket: DatagramSocket
    private lateinit var audioTrack: AudioTrack

    // ...
    fun registerWithServer(serverIp: String, serverRegistrationPort: Int, configData: String) {
        CoroutineScope(Dispatchers.IO).launch {
            val configData2 = "[screen_sharing]{keyenter}videoserverip = 192.168.31.194{keyenter}videoserverport = 12345{keyenter}peripheralserverip = 192.168.31.194{keyenter}peripheralserverport = 12346{keyenter}default_target_screen_width = 1920{keyenter}default_target_screen_height = 1080{keyenter}default_window_width = 800{keyenter}default_window_height = 600{keyenter}[audio_sharing]{keyenter}audioserverip = 192.168.31.194{keyenter}audioserverport = 5005{keyenter}channels = 2{keyenter}rate = 44100{keyenter}chunk = 1024{keyenter}deviceindex = 0{keyenter}deviceautotarget = CABLE Output"

            try {
                val socket = Socket(InetAddress.getByName(serverIp), serverRegistrationPort)

                val outputStream = socket.getOutputStream()
                // Send configuration
                outputStream.write(configData2.toByteArray())
                val terminator = byteArrayOf(0, 0, 0, 0)// Terminator sequence
                outputStream.write(terminator)
                outputStream.flush()


                socket.close()
            } catch (e: IOException) {

            }
            startReceiving(5005)
        }

    }




    fun startReceiving(serverPort: Int) {
        socket = DatagramSocket(serverPort)

        // Initialize AudioTrack outside the loop
        val audioAttributes = AudioAttributes.Builder()
            .setUsage(AudioAttributes.USAGE_MEDIA)
            .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
            .build()

        val audioFormat = AudioFormat.Builder()
            .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
            .setSampleRate(44100)
            .setChannelMask(AudioFormat.CHANNEL_OUT_STEREO)
            .build()

        val bufferSize = AudioTrack.getMinBufferSize(44100, AudioFormat.CHANNEL_OUT_STEREO, AudioFormat.ENCODING_PCM_16BIT)

        audioTrack = AudioTrack(
            audioAttributes,
            audioFormat,
            bufferSize,
            AudioTrack.MODE_STREAM,
            AudioManager.AUDIO_SESSION_ID_GENERATE
        )

        audioTrack.play() // Start playback

        Thread {
            val buffer = ByteArray(1024 * 2 * 2)
            val packet = DatagramPacket(buffer, buffer.size)

            while (true) {
                socket.receive(packet)

                // Write received data to the existing AudioTrack
                val byteBuffer = ByteBuffer.wrap(buffer)
                audioTrack.write(byteBuffer, buffer.size, AudioTrack.WRITE_BLOCKING)
            }
        }.start()
    }


    fun stopReceiving() {
        socket.close()
    }
}
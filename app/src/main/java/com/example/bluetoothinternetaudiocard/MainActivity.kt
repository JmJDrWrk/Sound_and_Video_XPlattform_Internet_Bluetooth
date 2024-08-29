package com.example.bluetoothinternetaudiocard

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import com.example.bluetoothinternetaudiocard.ui.theme.BluetoothInternetAudioCardTheme

class MainActivity : ComponentActivity() {
    private val audioReceiver = AudioReceiver() // Instantiate AudioReceiver

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        audioReceiver.registerWithServer( "192.168.31.194", 54424, "")

        enableEdgeToEdge()
        setContent {
            BluetoothInternetAudioCardTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    AudioStreamingScreen(
                        modifier = Modifier.padding(innerPadding),
                        audioReceiver = audioReceiver
                    )
                }
            }
        }
    }
}

@Composable
fun AudioStreamingScreen(
    modifier: Modifier = Modifier,
    audioReceiver: AudioReceiver
) {
    var isReceiving by remember { mutableStateOf(false) }

    Column(
        modifier = modifier.fillMaxSize(),
        verticalArrangement= Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        if (!isReceiving) {
            Button(onClick = {
                isReceiving = true
                audioReceiver.startReceiving(5000) // Replace with actual IP and port
            }) {
                Text("Start Receiving Audio")
            }
        } else {
            Button(onClick = {
                isReceiving = false
                audioReceiver.stopReceiving()
            }) {
                Text("Stop Receiving Audio")
            }
        }
    }
}
@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    BluetoothInternetAudioCardTheme {
        AudioStreamingScreen(audioReceiver = AudioReceiver())
    }
}
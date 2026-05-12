package network

import okhttp3.*
import okio.ByteString
import android.util.Log;

class WebSocketManager {

    private val client = OkHttpClient()

    private var webSocket: WebSocket? = null

    fun connect(
        onMessageReceived: (String) -> Unit
    ) {

        val request = Request.Builder()
            .url("ws://192.168.0.15:8000/ws")
            .build()

        webSocket = client.newWebSocket(
            request,
            object : WebSocketListener() {

                override fun onOpen(
                    webSocket: WebSocket,
                    response: Response
                ) {

                    println("WebSocket Connected")
                }


                override fun onMessage(
                    webSocket: WebSocket,
                    bytes: ByteString
                ) {

                    println(bytes.hex())
                }
                override fun onMessage(webSocket: WebSocket,text: String) {

                    Log.d("aaa", "WS MESSAGE: $text")
                    onMessageReceived(text)
                }

                override fun onClosing(
                    webSocket: WebSocket,
                    code: Int,
                    reason: String
                ) {

                    webSocket.close(1000, null)
                }

                override fun onFailure(
                    webSocket: WebSocket,
                    t: Throwable,
                    response: Response?
                ) {

                    println("WebSocket Error")
                    t.printStackTrace()
                }
            }
        )
    }

    fun disconnect() {

        webSocket?.close(1000, "Closing")
    }
}
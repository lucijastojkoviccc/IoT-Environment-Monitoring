package screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items

import androidx.compose.material3.*

import androidx.compose.runtime.*

import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

import network.Constants

import okhttp3.OkHttpClient
import okhttp3.Request

import org.json.JSONArray


data class HistoryItem(

    val brightness: Int,

    val contrast: Int,

    val predictedClass: String,

    val timestamp: String
)


@Composable
fun HistoryScreen(
    padding: PaddingValues
) {

    var historyItems by remember {

        mutableStateOf(
            emptyList<HistoryItem>()
        )
    }

    val client = remember {

        OkHttpClient()
    }


    LaunchedEffect(Unit) {

        CoroutineScope(Dispatchers.IO).launch {

            while (true) {

                try {

                    val request = Request.Builder()

                        .url(
                            "${Constants.BASE_HTTP}/api/history"
                        )

                        .build()

                    val response =
                        client.newCall(request)
                            .execute()

                    val body =
                        response.body?.string()

                    Log.d(
                        "HISTORY",
                        "BODY: $body"
                    )

                    if (body != null) {

                        val jsonArray =
                            JSONArray(body)

                        val tempList =
                            mutableListOf<HistoryItem>()

                        for (i in 0 until jsonArray.length()) {

                            val item =
                                jsonArray.getJSONObject(i)

                            tempList.add(

                                HistoryItem(

                                    brightness =
                                    item.optDouble(
                                        "brightness",
                                        0.0
                                    ).toInt(),

                                    contrast =
                                    item.optDouble(
                                        "contrast",
                                        0.0
                                    ).toInt(),

                                    predictedClass =
                                    item.optString(
                                        "light_state",
                                        "unknown"
                                    ),

                                    timestamp =
                                    item.optString(
                                        "timestamp",
                                        ""
                                    )
                                )
                            )
                        }

                        CoroutineScope(
                            Dispatchers.Main
                        ).launch {

                            historyItems =
                                tempList.reversed()
                        }
                    }

                } catch (e: Exception) {

                    Log.e(
                        "HISTORY",
                        "ERROR",
                        e
                    )
                }

                kotlinx.coroutines.delay(1000)
            }
        }
    }


    Column(

        modifier = Modifier
            .fillMaxSize()
            .padding(padding)
            .padding(16.dp)
    ) {

        Text(

            text = "History",

            style =
            MaterialTheme
                .typography
                .headlineMedium
        )

        Spacer(
            modifier =
            Modifier.height(16.dp)
        )

        LazyColumn (modifier = Modifier.weight(1f)) {



            items(historyItems) { item ->

                Card(

                    colors = CardDefaults.cardColors(

                        containerColor =
                        MaterialTheme.colorScheme.surfaceVariant
                    ),

                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp)
                ) {

                    Column(

                        modifier =
                        Modifier.padding(16.dp)
                    ) {

                        Text(
                            "Brightness: ${item.brightness}"
                        )

                        Text(
                            "Contrast: ${item.contrast}"
                        )

                        Text(
                            "Class: ${item.predictedClass}"
                        )

                        Text(
                            "Time: ${item.timestamp}"
                        )
                    }
                }
            }
        }
    }
}
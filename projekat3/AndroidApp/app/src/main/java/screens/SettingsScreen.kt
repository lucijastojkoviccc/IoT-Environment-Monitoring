package screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import android.widget.Toast
import androidx.compose.ui.platform.LocalContext

@Composable
fun SettingsScreen(padding: PaddingValues) {

    var brightnessThreshold by remember { mutableStateOf("100") }
    var contrastThreshold by remember { mutableStateOf("40") }
    var samplingInterval by remember { mutableStateOf("2") }

    val client = remember {

        OkHttpClient()
    }

    val context = LocalContext.current
    fun sendAction(action: String) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val json = JSONObject()
                json.put("action", action)

                val body = json.toString()
                    .toRequestBody("application/json".toMediaType())

                val request = Request.Builder()
                    .url("http://192.168.0.15:8000/api/action")
                    .post(body)
                    .build()

                val response = client.newCall(request).execute()

                CoroutineScope(Dispatchers.Main).launch {
                    if (response.isSuccessful) {
                        Toast.makeText(context, "$action sent", Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(context, "Action error: ${response.code}", Toast.LENGTH_SHORT).show()
                    }
                }

                response.close()

            } catch (e: Exception) {
                e.printStackTrace()

                CoroutineScope(Dispatchers.Main).launch {
                    Toast.makeText(context, "Failed to send action", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    Column(

        modifier = Modifier
            .fillMaxSize()
            .padding(padding)
            .padding(24.dp)
    ) {

        Text(
            text = "Settings & Control",
            style = MaterialTheme.typography.headlineMedium


        )

        Spacer(modifier = Modifier.height(24.dp))

        OutlinedTextField(
            value = brightnessThreshold,
            onValueChange = { brightnessThreshold = it },
            label = { Text("Brightness Threshold") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = contrastThreshold,
            onValueChange = { contrastThreshold = it },
            label = { Text("Contrast Threshold") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = samplingInterval,
            onValueChange = { samplingInterval = it },
            label = { Text("Sampling Interval") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(24.dp))

        Button(

            onClick = {

                CoroutineScope(Dispatchers.IO).launch {
                    try {
                        val json = JSONObject()

                        json.put("brightness_threshold", brightnessThreshold.toInt())
                        json.put("contrast_threshold", contrastThreshold.toInt())
                        json.put("sampling_interval", samplingInterval.toInt())

                        val body = json.toString()
                            .toRequestBody("application/json".toMediaType())

                        val request = Request.Builder()
                            .url("http://192.168.0.15:8000/api/config")
                            .post(body)
                            .build()

                        val response = client.newCall(request).execute()

                        CoroutineScope(Dispatchers.Main).launch {
                            if (response.isSuccessful) {
                                Toast.makeText(context, "Settings saved", Toast.LENGTH_SHORT).show()
                            } else {
                                Toast.makeText(context, "Error: ${response.code}", Toast.LENGTH_SHORT).show()
                            }
                        }

                        response.close()

                    } catch (e: Exception) {
                        e.printStackTrace()

                        CoroutineScope(Dispatchers.Main).launch {
                            Toast.makeText(context, "Failed to send settings", Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            },

            modifier = Modifier.fillMaxWidth()
        ) {

            Text("Save Settings")
        }

        Spacer(modifier = Modifier.height(32.dp))

        Text(
            text = "Actuator Control",
            style = MaterialTheme.typography.titleLarge
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(

            onClick = {

                sendAction("LED_ON")
            },

            modifier = Modifier.fillMaxWidth()
        ) {

            Text("Turn LED ON")
        }

        Spacer(modifier = Modifier.height(12.dp))

        Button(

            onClick = {

                sendAction("LED_OFF")
            },

            modifier = Modifier.fillMaxWidth()
        ) {

            Text("Turn LED OFF")
        }

        Spacer(modifier = Modifier.height(12.dp))

        Button(

            onClick = {

                sendAction("RESET")
            },

            modifier = Modifier.fillMaxWidth()
        ) {

            Text("Reset System")
        }
    }
}
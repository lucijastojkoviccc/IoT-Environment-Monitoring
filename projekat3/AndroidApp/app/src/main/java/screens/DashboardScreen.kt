package screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import network.WebSocketManager
import org.json.JSONObject
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

@Composable
fun DashboardScreen(padding: PaddingValues) {


    var brightness by remember { mutableStateOf(120) }
    var contrast by remember { mutableStateOf(45) }
    var predictedClass by remember { mutableStateOf("normal_light") }
    var timestamp by remember { mutableStateOf("No data") }
    val wsManager = remember {
        WebSocketManager()
    }

    LaunchedEffect(Unit) {

        wsManager.connect { message ->

            CoroutineScope(Dispatchers.Main).launch {

                val json = JSONObject(message)

                brightness =
                    json.getDouble("brightness").toInt()

                contrast =
                    json.getDouble("contrast").toInt()

                predictedClass =
                    json.getString("light_state")

                timestamp =
                    json.getString("timestamp")
            }
        }
    }



    Column(

        modifier = Modifier
            .fillMaxSize()
            .padding(padding)
            .padding(24.dp),

        verticalArrangement = Arrangement.Center,

        horizontalAlignment = Alignment.CenterHorizontally
    ) {

        Text(
            text = "IoT Dashboard",
            style = MaterialTheme.typography.headlineMedium
        )

        Spacer(modifier = Modifier.height(32.dp))

        Card(
            modifier = Modifier.fillMaxWidth()
        ) {

            Column(
                modifier = Modifier.padding(20.dp)
            ) {

                Text("Brightness: $brightness")

                Spacer(modifier = Modifier.height(8.dp))

                Text("Contrast: $contrast")

                Spacer(modifier = Modifier.height(8.dp))

                Text("Predicted class: $predictedClass")

                Spacer(modifier = Modifier.height(8.dp))

                Text("Timestamp: $timestamp")
            }
        }
    }
}

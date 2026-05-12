package model

data class SensorData(
    val brightness: Int,
    val contrast: Int,
    val predicted_class: String,
    val timestamp: String
)
package com.example.iotdashboard.navigation

import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.compose.*
import screens.DashboardScreen
import screens.HistoryScreen
import screens.SettingsScreen
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*

sealed class Screen(
    val route: String,
    val title: String,
    val icon: ImageVector
) {
    object Dashboard : Screen("dashboard", "Dashboard", Icons.Default.Home)
    object History : Screen("history", "History", Icons.Default.List)
    object Settings : Screen("settings", "Settings", Icons.Default.Settings)
}

@Composable
fun AppNavigation() {

    val navController = rememberNavController()

    val items = listOf(
        Screen.Dashboard,
        Screen.History,
        Screen.Settings
    )

    Scaffold(

        bottomBar = {

            NavigationBar {

                val currentRoute =
                    navController.currentBackStackEntryAsState().value
                        ?.destination?.route

                items.forEach { screen ->

                    NavigationBarItem(

                        selected = currentRoute == screen.route,

                        onClick = {
                            navController.navigate(screen.route)
                        },

                        icon = {
                            Icon(
                                imageVector = screen.icon,
                                contentDescription = screen.title
                            )
                        },

                        label = {
                            Text(screen.title)
                        }
                    )
                }
            }
        }

    ) { padding ->

        NavHost(
            navController = navController,
            startDestination = Screen.Dashboard.route
        ) {

            composable(Screen.Dashboard.route) {
                DashboardScreen(padding)
            }

            composable(Screen.History.route) {
                HistoryScreen(padding)
            }

            composable(Screen.Settings.route) {
                SettingsScreen(padding)
            }
        }
    }
}
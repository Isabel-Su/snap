import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import 'react-native-reanimated';
import { useFonts } from 'expo-font';

import { useColorScheme } from '@/hooks/use-color-scheme';

export const unstable_settings = {
  anchor: '(tabs)',
};

export default function RootLayout() {
  const colorScheme = useColorScheme();
  const [fontsLoaded] = useFonts({
    // Place the font files at reactFrontEnd/assets/fonts/
    'IndustryDemi': require('../assets/fonts/IndustryDemi-Regular.otf'),
    'IndustryDemi-Bold': require('../assets/fonts/IndustryDemi-Bold.otf'),
  });

  // Continue rendering the app even if fonts haven't loaded yet to avoid a
  // blank screen. Components will pick up the custom font when it finishes
  // loading. If you prefer a loading indicator, replace the line below.

  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <Stack>
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="modal" options={{ presentation: 'modal', title: 'Modal' }} />
      </Stack>
      <StatusBar style="auto" />
    </ThemeProvider>
  );
}

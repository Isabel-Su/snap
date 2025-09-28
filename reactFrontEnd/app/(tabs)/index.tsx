import React, { useRef, useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  Text,
  Pressable,
  Animated,
  Dimensions,
  Platform,
} from 'react-native';
import { ThemedText } from '@/components/themed-text';

const SCREEN_WIDTH = Dimensions.get('window').width;

export default function HomeScreen() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const sidebarWidth = Math.min(360, Math.round(SCREEN_WIDTH * 0.45));
  const anim = useRef(new Animated.Value(0)).current; // 0 closed, 1 open

  useEffect(() => {
    Animated.timing(anim, {
      toValue: sidebarOpen ? 1 : 0,
      duration: 300,
      useNativeDriver: true,
    }).start();
  }, [sidebarOpen, anim]);

  const translateX = anim.interpolate({
    inputRange: [0, 1],
    outputRange: [sidebarWidth, 0],
  });

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.titleContainer}>
          <ThemedText type="title" style={styles.title}>
            To Bet or Not to Bet?
          </ThemedText>
        </View>
        
        <Pressable
          onPress={() => setSidebarOpen(true)}
          accessibilityRole="button"
          accessibilityLabel="Open sidebar"
          style={styles.openButton}
        >
          <Text style={styles.openButtonText}>☰</Text>
        </Pressable>
      </View>

      <View style={styles.content}>
        <View
          style={styles.grayBox}
          accessibilityRole="image"
          accessibilityLabel="Placeholder gray box"
        />
      </View>

      {/* overlay when sidebar open */}
      {sidebarOpen && (
        <Pressable
          style={styles.overlay}
          onPress={() => setSidebarOpen(false)}
          accessibilityLabel="Close sidebar overlay"
        />
      )}

      <Animated.View
        style={[
          styles.sidebar,
          { width: sidebarWidth, transform: [{ translateX }] },
        ]}
      >
        <View style={styles.sidebarHeader}>
          <Text style={styles.sidebarTitle}>Saved Captions</Text>
          <Pressable
            onPress={() => setSidebarOpen(false)}
            accessibilityRole="button"
            accessibilityLabel="Close sidebar"
            style={styles.closeButton}
          >
            <Text style={styles.closeButtonText}>✕</Text>
          </Pressable>
        </View>

        <View style={styles.sidebarBody}>
          <Text style={styles.sidebarText}>Placeholder sidebar content</Text>
        </View>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000ff',
  },
  header: {
    width: '100%',
    backgroundColor: '#000000ff',
    paddingVertical: 14,
    paddingHorizontal: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },

  // Title color (To Bet or Not to Bet?)
  title: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '700',
  },
  
  // Background for title
  titleContainer: {
    backgroundColor: 'rgba(41, 41, 41, 0.83)',
    paddingHorizontal: 900,
    paddingVertical: 10,
    paddingTop: 0,
    paddingBottom: 14,
    borderRadius: 0,
  },
  openButton: {
    position: 'absolute',
    right: 12,
    top: Platform.select({ ios: 12, android: 12, default: 12 }),
    padding: 8,
  },
  openButtonText: {
    color: '#fff',
    fontSize: 20,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  grayBox: {
    width: 720,
    maxWidth: '95%',
    height: 420,
    backgroundColor: '#696969',
    borderRadius: 10,
    shadowColor: '#000',
    shadowOpacity: 0.18,
    shadowRadius: 10,
    elevation: 6,
  },

  /* Sidebar */
  sidebar: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    right: 0,
    backgroundColor: '#696969',
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 8,
    zIndex: 50,
  },
  sidebarHeader: {
    height: 56,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 12,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: 'rgba(0,0,0,0.15)',
  },
  sidebarTitle: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 16,
  },
  closeButton: {
    padding: 6,
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 18,
  },
  sidebarBody: {
    padding: 12,
  },
  sidebarText: {
    color: '#fff',
  },

  overlay: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(0,0,0,0.25)',
    zIndex: 40,
  },
});

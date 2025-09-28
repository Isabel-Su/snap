import * as React from 'react';
import {
  Animated,
  Pressable,
  StyleSheet,
  Text,
  View,
  Dimensions,
} from 'react-native';

const { width } = Dimensions.get('window');

export default function HomeScreen() {
  const slide = React.useRef(new Animated.Value(-width * 0.6)).current; // sidebar hidden to left

  function openSidebar() {
    Animated.timing(slide, {
      toValue: 0,
      duration: 250,
      useNativeDriver: true,
    }).start();
  }

  function closeSidebar() {
    Animated.timing(slide, {
      toValue: -width * 0.6,
      duration: 200,
      useNativeDriver: true,
    }).start();
  }

  return (
    <View style={styles.root}>
      <Animated.View style={[styles.sidebar, { transform: [{ translateX: slide }] }]}>
        <View style={styles.sidebarHeader}>
          <Text style={styles.sidebarTitle}>Saved captions</Text>
        </View>
        {/* Placeholder list */}
        <View style={styles.sidebarContent}>
          <Text style={styles.sidebarItem}>Caption 1</Text>
          <Text style={styles.sidebarItem}>Caption 2</Text>
          <Text style={styles.sidebarItem}>Caption 3</Text>
        </View>
        <Pressable style={styles.closeButton} onPress={closeSidebar} accessibilityLabel="Close sidebar">
          <Text style={styles.closeText}>Close</Text>
        </Pressable>
      </Animated.View>

      <View style={styles.header}>
        <Pressable onPress={openSidebar} style={styles.hamburger} accessibilityLabel="Open Saved captions">
          <View style={styles.line} />
          <View style={styles.line} />
          <View style={styles.line} />
        </Pressable>
        <View style={styles.titleWrapper}>
          <View style={styles.titleBackground} />
          <Text style={styles.title}>to bet or not to bet?</Text>
        </View>
      </View>

      <View style={styles.centerBox}>
        <View style={styles.grayRect} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#000',
  },
  header: {
    height: 80,
    paddingHorizontal: 16,
    alignItems: 'center',
    flexDirection: 'row',
  },
  hamburger: {
    padding: 8,
  },
  line: {
    width: 28,
    height: 3,
    backgroundColor: '#fff',
    marginVertical: 3,
    borderRadius: 2,
  },
  titleWrapper: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  titleBackground: {
    position: 'absolute',
    backgroundColor: '#2f2f2f',
    height: 40,
    width: '100%',
    borderRadius: 6,
    opacity: 0.95,
  },
  title: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '700',
    paddingHorizontal: 12,
  },
  centerBox: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  grayRect: {
    width: '80%',
    height: 300,
    backgroundColor: '#333',
    borderRadius: 12,
  },
  sidebar: {
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    width: width * 0.6,
    backgroundColor: '#111',
    shadowColor: '#000',
    shadowOpacity: 0.7,
    shadowRadius: 8,
    elevation: 10,
    paddingTop: 40,
    zIndex: 100,
  },
  sidebarHeader: {
    paddingHorizontal: 16,
    paddingBottom: 12,
  },
  sidebarTitle: {
    color: '#ddd',
    fontSize: 18,
    fontWeight: '700',
  },
  sidebarContent: {
    paddingHorizontal: 16,
    paddingTop: 8,
  },
  sidebarItem: {
    color: '#bbb',
    paddingVertical: 8,
  },
  closeButton: {
    marginTop: 24,
    padding: 12,
    alignSelf: 'center',
  },
  closeText: {
    color: '#fff',
  },
});
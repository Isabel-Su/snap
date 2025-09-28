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
  const sidebarWidth = width * 0.4; // reduced size
  const slide = React.useRef(new Animated.Value(sidebarWidth)).current;
  const backdrop = React.useRef(new Animated.Value(0)).current;
  const [isOpen, setIsOpen] = React.useState(false);

  function openSidebar() {
    setIsOpen(true);
    Animated.timing(slide, {
      toValue: 0,
      duration: 250,
      useNativeDriver: true,
    }).start();
    Animated.timing(backdrop, {
      toValue: 0.5,
      duration: 250,
      useNativeDriver: true,
    }).start();
  }

  function closeSidebar() {
    // Keep isOpen true until animations finish so backdrop can fade out
    Animated.parallel([
      Animated.timing(slide, {
        toValue: sidebarWidth,
        duration: 200,
        useNativeDriver: true,
      }),
      Animated.timing(backdrop, {
        toValue: 0,
        duration: 200,
        useNativeDriver: true,
      }),
    ]).start(() => {
      setIsOpen(false);
    });
  }

  return (
    <View style={styles.root}>
      {isOpen && (
        <Animated.View style={[styles.backdrop, { opacity: backdrop }]}>
          <Pressable style={{ flex: 1 }} onPress={closeSidebar} accessibilityLabel="Close Saved captions" />
        </Animated.View>
      )}

      <Animated.View style={[styles.sidebar, { width: sidebarWidth, transform: [{ translateX: slide }] }]}>
        <View style={styles.sidebarHeader}>
          <Text style={styles.sidebarTitle}>Saved Captions:</Text>
        </View>
        {/* Placeholder list */}
        <View style={styles.sidebarContent}>
          <Text style={styles.sidebarItem}>Caption 1</Text>
          <Text style={styles.sidebarItem}>Caption 2</Text>
          <Text style={styles.sidebarItem}>Caption 3</Text>
        </View>

      </Animated.View>

      <View style={styles.header}>
        <View style={styles.titleWrapper}>
          <View style={styles.titleBackground} />
          <Text style={styles.title}>to bet or not to bet?</Text>
        </View>
        <Pressable onPress={() => (isOpen ? closeSidebar() : openSidebar())} style={styles.hamburgerRight} accessibilityLabel="Toggle Saved captions">
          <View style={styles.line} />
          <View style={styles.line} />
          <View style={styles.line} />
        </Pressable>
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
    right: 0,
    top: 0,
    bottom: 0,
    backgroundColor: '#333',
    shadowColor: '#000',
    shadowOpacity: 0.7,
    shadowRadius: 8,
    elevation: 10,
    paddingTop: 40,
    zIndex: 100,
  },
  backdrop: {
    position: 'absolute',
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    backgroundColor: '#000',
    zIndex: 90,
  },
  hamburgerRight: {
    padding: 8,
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
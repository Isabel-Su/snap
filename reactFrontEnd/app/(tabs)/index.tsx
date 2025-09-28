import * as React from 'react';
import {
  Animated,
  Pressable,
  StyleSheet,
  Text,
  View,
  Dimensions,
  Platform,
  Image,
} from 'react-native';
import { useEffect, useState } from 'react';

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
          <Text style={styles.title}>To Bet or Not to Bet?</Text>
        </View>
        <Pressable onPress={() => (isOpen ? closeSidebar() : openSidebar())} style={styles.hamburgerRight} accessibilityLabel="Toggle Saved captions">
          <View style={styles.line} />
          <View style={styles.line} />
          <View style={styles.line} />
        </Pressable>
      </View>

      <View style={styles.centerBox}>
        {Platform.OS === 'web' ? (
          <WebChart />
        ) : (
          <Image
            source={{
              uri: 'http://128.61.124.100:8000/impact_chart.gif'
            }}
            style={styles.chartImage}
            resizeMode="contain"
          />
        )}
      </View>
    </View>
  );
}

function WebChart() {
  const [points, setPoints] = useState<Array<any>>([]);
  const [meta, setMeta] = useState<any | null>(null);

  useEffect(() => {
    // Start by fetching meta (start/end/ymin/ymax)
    fetch('http://localhost:8000/impact_chart.json')
      .then((r) => r.json())
      .then(setMeta)
      .catch(() => setMeta(null));

    const evt = new EventSource('http://localhost:8000/impact_chart/stream?interval_ms=600');
    evt.onmessage = (e) => {
      try {
        const d = JSON.parse(e.data);
        setPoints((p) => [...p, d]);
      } catch (err) {
        // ignore
      }
    };
    evt.addEventListener('done', () => {
      evt.close();
    });
    evt.onerror = () => {
      evt.close();
    };
    return () => evt.close();
  }, []);

  if (!meta) {
    return <View style={[styles.chartImage, { alignItems: 'center', justifyContent: 'center' }]}><Text style={{ color: '#ddd' }}>Connecting…</Text></View>;
  }

  const w = 800;
  const h = 300;
  const pad = 40;
  const xScale = (v: number) => pad + ((v - meta.start) / (meta.end - meta.start)) * (w - pad * 2);
  const yScale = (v: number) => h - pad - ((v - meta.ymin) / (meta.ymax - meta.ymin)) * (h - pad * 2);

  const tpiPath = points.map((pt, i) => `${i === 0 ? 'M' : 'L'} ${xScale(pt.elapsed)} ${yScale(pt.tpi)}`).join(' ');
  const ppiPath = points.map((pt, i) => `${i === 0 ? 'M' : 'L'} ${xScale(pt.elapsed)} ${yScale(pt.ppi)}`).join(' ');

  const formatMMSS = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  };

  // x-axis ticks: major every 300s, minor every 60s
  const xMajor: number[] = [];
  for (let t = meta.start; t <= meta.end; t += 300) xMajor.push(t);
  const xMinor: number[] = [];
  for (let t = meta.start; t <= meta.end; t += 60) xMinor.push(t);

  // y-axis ticks (5 ticks)
  const yTicks: number[] = [];
  const yCount = 5;
  for (let i = 0; i < yCount; i++) {
    yTicks.push(meta.ymin + (i / (yCount - 1)) * (meta.ymax - meta.ymin));
  }

  return (
    <div style={{ width: '80%', maxWidth: 900 }}>
      <svg width="100%" viewBox={`0 0 ${w} ${h}`} style={{ backgroundColor: '#111', borderRadius: 8 }}>
        <rect x="0" y="0" width={w} height={h} fill="#111" />
        {/* Chart title */}
        <text x={w / 2} y={20} textAnchor="middle" fontSize={18} fontWeight={700} fill="#fff">Player Impact</text>

        {/* grid lines and y ticks */}
        <g>
          {yTicks.map((yt, i) => {
            const yy = yScale(yt);
            return (
              <g key={`y${i}`}>
                <line x1={pad} x2={w - pad} y1={yy} y2={yy} stroke="#2a2a2a" strokeWidth={1} />
                <text x={8} y={yy + 4} fontSize={12} fill="#bbb">{yt.toFixed(2)}</text>
              </g>
            );
          })}
        </g>

        {/* x-axis grid & ticks */}
        <g>
          {xMinor.map((xm, i) => {
            const xx = xScale(xm);
            return <line key={`xm${i}`} x1={xx} x2={xx} y1={h - pad + 4} y2={h - pad + 8} stroke="#444" strokeWidth={1} />;
          })}
          {xMajor.map((xm, i) => {
            const xx = xScale(xm);
            return (
              <g key={`xM${i}`}>
                <line x1={xx} x2={xx} y1={h - pad} y2={pad} stroke="#2a2a2a" strokeWidth={1} />
                <text x={xx - 18} y={h - pad + 18} fontSize={12} fill="#ddd">{formatMMSS(xm - meta.start)}</text>
              </g>
            );
          })}
        </g>

        {/* axis labels */}
        <g>
          <text x={w / 2} y={h - 6} textAnchor="middle" fontSize={13} fill="#ddd">Game Time (MM:SS elapsed)</text>
          <text transform={`translate(${12}, ${h / 2}) rotate(-90)`} textAnchor="middle" fontSize={13} fill="#ddd">Performance Index</text>
        </g>

        {/* plotted data */}
        <g>
          <path d={tpiPath} stroke="#4fa3ff" strokeWidth={2} fill="none" />
          <path d={ppiPath} stroke="#ff6b6b" strokeWidth={2} strokeDasharray="6 4" fill="none" />
          {points.length > 0 && (
            <circle cx={xScale(points[points.length - 1].elapsed)} cy={yScale(points[points.length - 1].tpi)} r={4} fill="#fff" />
          )}
        </g>
      </svg>
    </div>
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
  chartImage: {
    width: '80%',
    height: 300,
    borderRadius: 12,
    backgroundColor: '#333',
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
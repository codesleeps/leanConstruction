import React, { useState, useEffect } from 'react';
import { View, ScrollView, StyleSheet, RefreshControl } from 'react-native';
import { Card, Text, ActivityIndicator } from 'react-native-paper';
import { LineChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';
import { getDashboardData } from '../services/api';

const screenWidth = Dimensions.get('window').width;

export default function DashboardScreen() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [data, setData] = useState(null);

  const loadData = async () => {
    try {
      const dashboardData = await getDashboardData();
      setData(dashboardData);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleLarge">Project Health</Text>
          <View style={styles.statsRow}>
            <View style={styles.stat}>
              <Text variant="headlineMedium">{data?.activeProjects || 0}</Text>
              <Text variant="bodySmall">Active Projects</Text>
            </View>
            <View style={styles.stat}>
              <Text variant="headlineMedium">{data?.completionRate || 0}%</Text>
              <Text variant="bodySmall">Avg Completion</Text>
            </View>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleLarge">Waste Detection (24h)</Text>
          <View style={styles.statsRow}>
            <View style={styles.stat}>
              <Text variant="headlineMedium">{data?.wasteIncidents || 0}</Text>
              <Text variant="bodySmall">Incidents</Text>
            </View>
            <View style={styles.stat}>
              <Text variant="headlineMedium">${data?.wasteCost || 0}</Text>
              <Text variant="bodySmall">Cost Impact</Text>
            </View>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleLarge">Weekly Trend</Text>
          <LineChart
            data={{
              labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
              datasets: [{
                data: data?.weeklyTrend || [20, 45, 28, 80, 99, 43, 50]
              }]
            }}
            width={screenWidth - 60}
            height={220}
            chartConfig={{
              backgroundColor: '#2196F3',
              backgroundGradientFrom: '#2196F3',
              backgroundGradientTo: '#1976D2',
              decimalPlaces: 0,
              color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
              style: {
                borderRadius: 16
              }
            }}
            bezier
            style={styles.chart}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleLarge">Recent Alerts</Text>
          {data?.alerts?.map((alert, index) => (
            <View key={index} style={styles.alert}>
              <Text variant="bodyMedium">{alert.message}</Text>
              <Text variant="bodySmall" style={styles.alertTime}>
                {alert.time}
              </Text>
            </View>
          )) || (
            <Text variant="bodyMedium" style={styles.noData}>
              No recent alerts
            </Text>
          )}
        </Card.Content>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  card: {
    margin: 10,
    elevation: 2,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 15,
  },
  stat: {
    alignItems: 'center',
  },
  chart: {
    marginVertical: 10,
    borderRadius: 16,
  },
  alert: {
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  alertTime: {
    color: '#666',
    marginTop: 5,
  },
  noData: {
    textAlign: 'center',
    color: '#666',
    marginTop: 10,
  },
});

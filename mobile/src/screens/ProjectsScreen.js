import React, { useState, useEffect } from 'react';
import { View, FlatList, StyleSheet, RefreshControl } from 'react-native';
import { Card, Text, ActivityIndicator, Chip } from 'react-native-paper';
import { getProjects } from '../services/api';

export default function ProjectsScreen({ navigation }) {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [projects, setProjects] = useState([]);

  const loadProjects = async () => {
    try {
      const data = await getProjects();
      setProjects(data);
    } catch (error) {
      console.error('Error loading projects:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    loadProjects();
  };

  const renderProject = ({ item }) => (
    <Card
      style={styles.card}
      onPress={() => navigation.navigate('ProjectDetail', { project: item })}
    >
      <Card.Content>
        <View style={styles.header}>
          <Text variant="titleMedium">{item.name}</Text>
          <Chip mode="outlined" compact>
            {item.status}
          </Chip>
        </View>
        <Text variant="bodySmall" style={styles.description}>
          {item.description}
        </Text>
        <View style={styles.stats}>
          <Text variant="bodySmall">Budget: ${item.budget?.toLocaleString()}</Text>
          <Text variant="bodySmall">Progress: {item.progress || 0}%</Text>
        </View>
      </Card.Content>
    </Card>
  );

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={projects}
        renderItem={renderProject}
        keyExtractor={(item) => item.id.toString()}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <Text style={styles.empty}>No projects found</Text>
        }
      />
    </View>
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  description: {
    color: '#666',
    marginBottom: 10,
  },
  stats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 5,
  },
  empty: {
    textAlign: 'center',
    marginTop: 50,
    color: '#666',
  },
});

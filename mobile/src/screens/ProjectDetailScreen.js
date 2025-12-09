import React from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Card, Text, Button } from 'react-native-paper';

export default function ProjectDetailScreen({ route, navigation }) {
  const { project } = route.params;

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleLarge">{project.name}</Text>
          <Text variant="bodyMedium" style={styles.description}>
            {project.description}
          </Text>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium">Project Stats</Text>
          <View style={styles.stat}>
            <Text>Budget:</Text>
            <Text>${project.budget?.toLocaleString()}</Text>
          </View>
          <View style={styles.stat}>
            <Text>Status:</Text>
            <Text>{project.status}</Text>
          </View>
        </Card.Content>
      </Card>

      <Button
        mode="contained"
        style={styles.button}
        onPress={() => navigation.navigate('WasteLog', { projectId: project.id })}
      >
        Log Waste
      </Button>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  card: {
    margin: 10,
  },
  description: {
    marginTop: 10,
    color: '#666',
  },
  stat: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 10,
  },
  button: {
    margin: 10,
  },
});

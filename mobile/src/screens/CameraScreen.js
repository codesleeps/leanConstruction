import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Button } from 'react-native-paper';

export default function CameraScreen() {
  return (
    <View style={styles.container}>
      <Text variant="titleLarge">Site Photo Capture</Text>
      <Text variant="bodyMedium" style={styles.subtitle}>
        Camera integration coming soon
      </Text>
      <Button mode="contained" style={styles.button}>
        Take Photo
      </Button>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  subtitle: {
    marginTop: 10,
    marginBottom: 20,
    color: '#666',
  },
  button: {
    marginTop: 20,
  },
});

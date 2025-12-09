import React, { useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { TextInput, Button, Text, Snackbar } from 'react-native-paper';
import { Picker } from '@react-native-picker/picker';
import { createWasteLog } from '../services/api';

const WASTE_TYPES = [
  { label: 'Defects', value: 'defects' },
  { label: 'Overproduction', value: 'overproduction' },
  { label: 'Waiting', value: 'waiting' },
  { label: 'Non-Utilized Talent', value: 'non_utilized_talent' },
  { label: 'Transportation', value: 'transportation' },
  { label: 'Inventory', value: 'inventory' },
  { label: 'Motion', value: 'motion' },
  { label: 'Extra Processing', value: 'extra_processing' },
];

export default function WasteLogScreen({ route, navigation }) {
  const { projectId } = route.params;
  const [wasteType, setWasteType] = useState('defects');
  const [description, setDescription] = useState('');
  const [impactCost, setImpactCost] = useState('');
  const [impactTime, setImpactTime] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async () => {
    if (!description || !impactCost || !impactTime) {
      setMessage('Please fill all fields');
      return;
    }

    setLoading(true);
    try {
      await createWasteLog(projectId, {
        waste_type: wasteType,
        description,
        impact_cost: parseFloat(impactCost),
        impact_time: parseFloat(impactTime),
      });
      setMessage('Waste logged successfully');
      setTimeout(() => navigation.goBack(), 1500);
    } catch (error) {
      setMessage('Error logging waste');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text variant="titleMedium" style={styles.label}>
          Waste Type
        </Text>
        <Picker
          selectedValue={wasteType}
          onValueChange={setWasteType}
          style={styles.picker}
        >
          {WASTE_TYPES.map((type) => (
            <Picker.Item key={type.value} label={type.label} value={type.value} />
          ))}
        </Picker>

        <TextInput
          label="Description"
          value={description}
          onChangeText={setDescription}
          mode="outlined"
          multiline
          numberOfLines={4}
          style={styles.input}
        />

        <TextInput
          label="Impact Cost ($)"
          value={impactCost}
          onChangeText={setImpactCost}
          mode="outlined"
          keyboardType="numeric"
          style={styles.input}
        />

        <TextInput
          label="Impact Time (hours)"
          value={impactTime}
          onChangeText={setImpactTime}
          mode="outlined"
          keyboardType="numeric"
          style={styles.input}
        />

        <Button
          mode="contained"
          onPress={handleSubmit}
          loading={loading}
          disabled={loading}
          style={styles.button}
        >
          Submit
        </Button>
      </View>

      <Snackbar
        visible={!!message}
        onDismiss={() => setMessage('')}
        duration={3000}
      >
        {message}
      </Snackbar>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: 20,
  },
  label: {
    marginBottom: 10,
  },
  picker: {
    backgroundColor: 'white',
    marginBottom: 15,
  },
  input: {
    marginBottom: 15,
  },
  button: {
    marginTop: 10,
  },
});

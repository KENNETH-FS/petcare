import { FlatList, Pressable, Text, View } from "react-native";

type SlotListProps = {
  slots: string[];
  onSelectSlot: (slot: string) => void;
};

export function SlotList({ slots, onSelectSlot }: SlotListProps) {
  if (slots.length === 0) {
    return (
      <View>
        <Text>No available slots for this date.</Text>
      </View>
    );
  }

  return (
    <FlatList
      data={slots}
      keyExtractor={(slot) => slot}
      renderItem={({ item }) => (
        <Pressable onPress={() => onSelectSlot(item)}>
          <Text>{formatSlotTime(item)}</Text>
        </Pressable>
      )}
    />
  );
}

function formatSlotTime(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}
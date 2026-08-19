import { useEffect, useState } from "react";
import { ActivityIndicator, Text, View } from "react-native";

import { getAvailableSlots } from "../client";
import { SlotList } from "../components/SlotList";

type BookingScreenProps = {
  clinicId: number;
  date: string;
  onSelectSlot: (slot: string) => void;
};

type LoadState =
  | { status: "loading" }
  | { status: "success"; slots: string[] }
  | { status: "error"; message: string };

export function BookingScreen({ clinicId, date, onSelectSlot }: BookingScreenProps) {
  const [state, setState] = useState<LoadState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;
    setState({ status: "loading" });

    getAvailableSlots(clinicId, date)
      .then((slots) => {
        if (!cancelled) setState({ status: "success", slots });
      })
      .catch((error: Error) => {
        if (!cancelled) setState({ status: "error", message: error.message });
      });

    return () => {
      cancelled = true;
    };
  }, [clinicId, date]);

  if (state.status === "loading") {
    return (
      <View>
        <ActivityIndicator testID="loading-indicator" />
        <Text>Loading available times…</Text>
      </View>
    );
  }

  if (state.status === "error") {
    return (
      <View>
        <Text>Couldn't load available times. Please try again.</Text>
      </View>
    );
  }

  return <SlotList slots={state.slots} onSelectSlot={onSelectSlot} />;
}
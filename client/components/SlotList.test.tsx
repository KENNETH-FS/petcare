import { fireEvent, render, screen } from "@testing-library/react-native";

import { SlotList } from "./SlotList";

const NINE_AM_UTC = "2027-06-01T09:00:00Z";
const expectedNineAmLabel = new Date(NINE_AM_UTC).toLocaleTimeString([], {
  hour: "2-digit",
  minute: "2-digit",
});

describe("SlotList", () => {
  it("renders each slot's formatted time", async () => {
    await render(
      <SlotList slots={[NINE_AM_UTC, "2027-06-01T09:30:00Z"]} onSelectSlot={() => {}} />
    );

    expect(screen.getByText(expectedNineAmLabel)).toBeTruthy();
  });

  it("shows an empty-state message when there are no slots", async () => {
    await render(<SlotList slots={[]} onSelectSlot={() => {}} />);

    expect(screen.getByText("No available slots for this date.")).toBeTruthy();
  });

  it("fires onSelectSlot with the pressed slot's value when tapped", async () => {
    const onSelectSlot = jest.fn();
    await render(<SlotList slots={[NINE_AM_UTC]} onSelectSlot={onSelectSlot} />);

    fireEvent.press(screen.getByText(expectedNineAmLabel));

    expect(onSelectSlot).toHaveBeenCalledWith(NINE_AM_UTC);
    expect(onSelectSlot).toHaveBeenCalledTimes(1);
  });
});
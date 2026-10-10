export const DATA = {
  "model": {
    "version": 1,
    "provenance": "Hand-authored synthetic preferences, not human observations",
    "rows": 81,
    "classes": {
      "pause": 28,
      "observe": 31,
      "wander": 18,
      "explore": 4
    },
    "counts": {
      "pause": {
        "time": {
          "5": 12,
          "15": 8,
          "30": 8
        },
        "energy": {
          "low": 15,
          "medium": 8,
          "high": 5
        },
        "setting": {
          "doorstep": 12,
          "street": 11,
          "park": 5
        }
      },
      "observe": {
        "time": {
          "5": 15,
          "15": 9,
          "30": 7
        },
        "energy": {
          "low": 10,
          "medium": 10,
          "high": 11
        },
        "setting": {
          "doorstep": 15,
          "street": 4,
          "park": 12
        }
      },
      "wander": {
        "time": {
          "15": 10,
          "30": 8
        },
        "energy": {
          "low": 2,
          "medium": 7,
          "high": 9
        },
        "setting": {
          "street": 12,
          "park": 6
        }
      },
      "explore": {
        "time": {
          "30": 4
        },
        "energy": {
          "medium": 2,
          "high": 2
        },
        "setting": {
          "park": 4
        }
      }
    }
  },
  "activities": {
    "pause": {
      "title": "Outdoor sensory pause",
      "minutes": 5,
      "instruction": "If safe, pause at an accessible outdoor spot. Notice three colors and two sounds. Sitting is fine."
    },
    "observe": {
      "title": "Nature noticing",
      "minutes": 5,
      "instruction": "From an accessible outdoor spot, observe a plant, cloud, or bird without approaching wildlife. No plant or animal identification is required."
    },
    "wander": {
      "title": "Gentle accessible wander",
      "minutes": 15,
      "instruction": "Choose a familiar, accessible route close to home. Walk or roll at your own pace; turn back early if needed."
    },
    "explore": {
      "title": "Longer park loop",
      "minutes": 30,
      "instruction": "Use a familiar marked accessible park route. Walk or roll gently, stay near an exit, and skip any section that feels unsafe."
    }
  },
  "features": [
    "time",
    "energy",
    "setting"
  ],
  "values": {
    "time": [
      "5",
      "15",
      "30"
    ],
    "energy": [
      "low",
      "medium",
      "high"
    ],
    "setting": [
      "doorstep",
      "street",
      "park"
    ]
  }
};

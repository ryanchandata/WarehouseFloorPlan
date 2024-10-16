<template>
    <div>
      <!-- New Header Section -->
      <div class="header">
        <div class="header-left">
          <div>Picking xx/xx 80% Used</div>
          <div>Storage xx/xx 80% Used</div>
        </div>
        <div class="header-center">
          <h1>Floor Plan Visualization</h1>
        </div>
        <div class="header-right">
          <button @click="toggleSettings" class="show-controls-button">Show Controls</button>
        </div>
      </div>
      <div v-if="showSettings">
        <label for="group-select">Group:</label>
        <select id="group-select" v-model="selectedGroup" @change="updateURL">
          <option v-for="group in groups" :key="group" :value="group">{{ group }}</option>
        </select>
  
        <label for="x-mirror-select">X Mirror:</label>
        <select id="x-mirror-select" v-model="xMirrorMode" @change="updateURL">
          <option value="standard">Standard</option>
          <option value="mirror">Mirror</option>
        </select>
  
        <label for="y-mirror-select">Y Mirror:</label>
        <select id="y-mirror-select" v-model="yMirrorMode" @change="updateURL">
          <option value="standard">Standard</option>
          <option value="mirror">Mirror</option>
        </select>
  
        <div id="z-index-controls">
          <label v-for="index in availableZIndices" :key="index">
            <input type="checkbox" :value="index" v-model="selectedZIndices" @change="updateURL" /> Z {{ index }}
          </label>
        </div>
  
        <label for="ware-id-select">Ware ID:</label>
        <select id="ware-id-select" v-model="wareId" @change="updateURL">
          <option value="291">291</option>
          <!-- Add other options as necessary -->
        </select>
      </div>
  
      <div id="floor-plan" class="floor-plan" :style="gridStyle">
        <div v-if="filteredLocations.length === 0">No locations available for the selected group.</div>
        <div v-for="location in floorPlanCells" :key="location.key" :style="location.style" class="location">
  <div
    v-for="item in location.items"
    :key="item.key"
    :class="item.class"
    :title="item.tooltip"
    :data-z="item.z"
  >
    <strong>{{ item.cellCode }}</strong><br />
    <span v-if="item.itemCode">{{ item.itemCode }}<br />Qty: {{ item.qty }}</span>
  </div>
  
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        locationData: [],
        groups: [],
        selectedGroup: '',
        xMirrorMode: 'standard',
        yMirrorMode: 'standard',
        availableZIndices: ['1', '2', '3'],
        selectedZIndices: ['1', '2', '3'],
        wareId: '291',
        inventoryData: [],
        showSettings: false
      };
    },
    computed: {
      filteredLocations() {
        return this.locationData.filter(loc => loc.area_code === this.selectedGroup);
      },
      maxCoordinates() {
        return {
          maxX: Math.max(...this.filteredLocations.map(loc => parseInt(loc.X, 10))),
          maxY: Math.max(...this.filteredLocations.map(loc => parseInt(loc.Y, 10))),
          maxZ: Math.max(...this.filteredLocations.map(loc => parseInt(loc.Z, 10)))
        };
      },
      gridStyle() {
        return {
          gridTemplateColumns: `repeat(${this.maxCoordinates.maxX}, 1fr)`
        };
      },
      floorPlanCells() {
        const cells = [];
        for (let y = 1; y <= this.maxCoordinates.maxY; y++) {
          const actualY = this.yMirrorMode === 'mirror' ? this.maxCoordinates.maxY - y + 1 : y;
          for (let x = 1; x <= this.maxCoordinates.maxX; x++) {
            const actualX = this.xMirrorMode === 'mirror' ? this.maxCoordinates.maxX - x + 1 : x;
            const locations = this.filteredLocations.filter(
              loc => parseInt(loc.X, 10) === x && parseInt(loc.Y, 10) === y
            ).sort((a, b) => parseInt(b.Z, 10) - parseInt(a.Z, 10));
  
            const items = locations
              .filter(location => this.selectedZIndices.includes(location.Z))
              .map(location => ({
                key: `${location.cell_code}-${location.Z}`,
                class: [
                  'location-item',
                  location.Status === 'disable' ? 'disable' : '',
                  location.itemCode ? 'has-inventory' : 'empty'
                ],
                tooltip: this.createTooltipContent(location),
                cellCode: location.cell_code,
                itemCode: location.itemCode,
                qty: location.qty,
                z: location.Z // Ensure `z` is assigned correctly
              }));
  
            cells.push({
              key: `${actualX}-${actualY}`,
              style: { gridColumn: actualX, gridRow: actualY },
              items
            });
          }
        }
        return cells;
      }
    },
    methods: {
      toggleSettings() {
        this.showSettings = !this.showSettings;
      },
      updateFloorPlan() {
        // Your logic to update the floor plan goes here.
        // This could involve re-rendering components or recalculating data bindings.
        console.log('Floor plan updated.');
      },
      async fetchData() {
        try {
          const locationsResponse = await fetch('locations.csv');
          const locationsText = await locationsResponse.text();
          this.locationData = this.parseCSV(locationsText);
  
          const inventoryResponse = await fetch(
            `http://localhost:3001/api/inventory?ware_id=${this.wareId}`
          );
          this.inventoryData = await inventoryResponse.json();
          this.updateLocationDataWithInventory();
  
          this.groups = [...new Set(this.locationData.map(loc => loc.area_code))].filter(area => area);
          this.selectedGroup = this.groups[0] || '';
        } catch (error) {
          console.error('Error loading data:', error);
        }
      },
      parseCSV(text) {
        const [headerLine, ...lines] = text.split('\n');
        const headers = headerLine.split(',').map(header => header.trim());
        return lines.map(line => {
          const values = line.split(',').map(value => value.trim());
          return headers.reduce((obj, header, index) => {
            obj[header] = values[index] || '';
            return obj;
          }, {});
        });
      },
      updateLocationDataWithInventory() {
        this.inventoryData.forEach(item => {
          const location = this.locationData.find(loc => loc['cell_code'] === item['cell_code']);
          if (location) {
            Object.assign(location, {
              itemCode: item['item_code'],
              itemName: item['item_name'],
              qty: item['quantity'],
              batchInfo: item['batch_info'] || []
            });
          }
        });
      },
      updateURL() {
        const params = new URLSearchParams();
        params.append('group', this.selectedGroup);
        params.append('xMirror', this.xMirrorMode);
        params.append('yMirror', this.yMirrorMode);
        params.append('zIndices', this.selectedZIndices.join(','));
        params.append('ware_id', this.wareId);
  
        const newUrl = `${window.location.pathname}?${params.toString()}`;
        window.history.pushState({}, '', newUrl);
        this.updateFloorPlan();
      },
      createTooltipContent(location) {
        const skuCode = location.itemCode || 'N/A';
        const skuName = location.itemName || 'N/A';
        const totalQty = location.qty || 0;
        const batchInfo = location.batchInfo || [];
        const batchInfoString = batchInfo
          .map(batch => `${batch.batchNo}  ${batch.expireDate}  ${batch.qty}`)
          .join('<br>');
  
        return `
          SKU ${skuCode}<br>
          Name: ${skuName}<br>
          Total: ${totalQty}<br>
          Batch Info:<br>
          Batch no            Expire_Date     Qty  <br>
          ${batchInfoString}
        `;
      },
      setInitialValuesFromPOST(data) {
        const group = data.get('group');
        const xMirror = data.get('xMirror');
        const yMirror = data.get('yMirror');
        const zIndices = data.get('zIndices') ? data.get('zIndices').split(',') : this.availableZIndices;
        this.wareId = data.get('ware_id') || '291';
  
        if (group) this.selectedGroup = group;
        if (xMirror) this.xMirrorMode = xMirror;
        if (yMirror) this.yMirrorMode = yMirror;
        this.selectedZIndices = zIndices;
      }
    },
    mounted() {
      this.fetchData();
      const formData = new URLSearchParams(window.location.search);
      this.setInitialValuesFromPOST(formData);
    }
  };
  </script>
  
  <style scoped>
  .floor-plan {
      display: grid;
      gap: 10px;
      padding: 20px;
      max-width: 100%;
      overflow-x: auto;
      border: 1px solid #ddd;
      border-radius: 8px;
      background-color: #fff;
  }
  
  .location {
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      align-items: center;
      font-size: 12px;
      text-align: center;
      position: relative;
      border: 1px solid #ccc;
      padding: 5px;
      background: #f9f9f9;
  }
  
  .z-level {
      display: flex;
      justify-content: center;
      align-items: center;
      width: 100%;
      min-height: 40px;
  }
  
  .location-item {
      width: 100%;
      min-width: 100px;
      padding: 8px;
      border: 1px solid #999;
      border-radius: 6px;
      background-color: #f0f0f0;
      box-sizing: border-box;
      font-size: 11px;
      line-height: 1.4;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-bottom: 5px;
  }
  
  .location-item[data-z="2"] {
      background-color: #d0d0ff;
  }
  
  .location-item[data-z="3"] {
      background-color: #ffd0d0;
  }
  
  .location-item.has-inventory {
      background-color: #a5d6a7;
      color: #1b5e20;
      height: 70px;
  }
  
  .location-item.has-inventory[data-z="2"] {
      background-color: #ffcc80 !important;
      color: #e65100 !important;
  }
  
  .location-item.has-inventory[data-z="3"] {
      background-color: #90caf9 !important;
      color: #0d47a1 !important;
  }
  
  .location-item.disable {
      background-color: #e0e0e0;
      color: #666;
      border: 1px solid #bbb;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 70px;
      font-weight: bold;
      opacity: 0.6;
  }
  
  .location-item.empty {
      background-color: #f5f5f5;
      color: #999;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 70px;
      font-weight: normal;
      border: 1px dashed #ccc;
      opacity: 0.8;
  }
  
  .location-item strong {
      font-size: 13px;
  }
  
  .show-controls-button {
    padding: 10px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
    margin-bottom: 10px;
  }
  .show-controls-button:hover {
    background-color: #0056b3;
  }
  </style>

  <style scoped>
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px; /* Add some space below the header */
  }

  .header-left, .header-center, .header-right {
    flex: 1; /* Allow equal space distribution */
  }

  .header-center {
    text-align: center; /* Center the title */
  }

  .header-left, .header-right {
    text-align: left; /* Align left and right sections */
  }

  .header-right {
    text-align: right; /* Align left and right sections */
  }
  </style>

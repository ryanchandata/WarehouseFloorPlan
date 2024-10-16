<template>
  <div id="app">
    <WarehouseFloorPlan />
  </div>
</template>

<script>
import WarehouseFloorPlan from './components/WarehouseFloorPlan.vue';

export default {
  name: 'App',
  components: {
    WarehouseFloorPlan
  }
};
</script>

<style>
body, html {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    font-family: Arial, sans-serif;
}

body {
    display: flex;
    flex-direction: column;
    background-color: #f0f2f5;
}

h1 {
    text-align: center;
    margin: 20px 0;
    color: #333;
}

.status-container {
    position: absolute;
    top: 2px;
    left: 10px;
    padding: 2px;
    border-radius: 5px;
    z-index: 1000;
}

.controls-container {
    position: absolute;
    top: 10px;
    right: 10px;
    background-color: transparent;
    border: none;
    padding: 0;
    z-index: 1000;
}

#controls {
    display: none;
    flex-direction: column;
    gap: 15px;
    background-color: #f9f9f9;
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 15px;
    margin-top: 10px;
}

#controls.show {
    display: flex;
}

.show-controls-button {
    padding: 10px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.show-controls-button:hover {
    background-color: #0056b3;
}

.separator-line {
    height: 4px;
    background-color: #f4b400;
    width: 100%;
    margin: 15px 0;
}

</style>

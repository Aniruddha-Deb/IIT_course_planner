<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { parse } from './parser/parser.js';

const program = ref(null);
const courses = ref([]);
const selectedCourse = ref('AM1');

async function update_table(course) {
  try {
    const response = await fetch(`data/programmes/${course}.json`);
    const data = await response.json();
    program.value = data;
    courses.value = Object.values(data.courses).flat();
  } catch (error) {
    console.error(error);
  }
}

watch(selectedCourse, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    update_table(newValue);
  }
});

onMounted(async () => {
  update_table(selectedCourse.value);
});

const recommended = computed(() => {
  return program.value ? program.value.recommended : [];
});
</script>

<template>
  <div id="app">
    <select v-model="selectedCourse">
      <option value="AM1">AM1</option>
      <option value="BB1">BB1</option>
      <option value="CE1">CE1</option>
      <option value="CH1">CH1</option>
      <option value="CH7">CH7</option>
      <option value="CS1">CS1</option>
      <option value="CS5">CS5</option>
      <option value="EE1">EE1</option>
      <option value="EE3">EE3</option>
      <option value="ES1">ES1</option>
      <option value="ME1">ME1</option>
      <option value="ME2">ME2</option>
      <option value="MS1">MS1</option>
      <option value="MT1">MT1</option>
      <option value="MT6">MT6</option>
      <option value="PH1">PH1</option>
      <option value="TT1">TT1</option>
    </select>
    <div class="course-container">
      <div class="course-row wrapper" v-for="(semester, index) in recommended" :key="index">
        <div class="course-label">Sem {{ index + 1 }}</div>
        <div class="course-cards container" v-dragula="semester" bag="schedule">
          <div class="course-card" v-for="courseCode in semester" :key="courseCode">{{ courseCode }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.course-container {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  width: 100%;
}

.course-row {
  display: flex;
  flex-direction: row;
  gap: 5px;
  width: 100%;
}

.course-label {
  padding: 8px;
  flex-weight: 1;
  text-align: center;
  writing-mode: vertical-lr;
  border: 1px solid black;
  border-radius: 5px 0 0 5px;
}

.course-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  width: 100%;
}

.course-card {
  width: 100px;
  height: 60px;
  padding: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 1px solid black;
  border-radius: 5px;
  user-select: none;
}

</style>

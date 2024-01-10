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
    <table>
      <tbody>
          <tr class="container" v-for="(semester, index) in recommended" :key="index">
          <td>Sem {{ index + 1 }}</td>
          <td>
              <div class="container" v-dragula="semester" bag="schedule">
                  <div class="course-card" v-for="courseCode in semester" :key="courseCode">{{courseCode}}</div>
              </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { parse } from './parser/parser.js';

// TODO rendering dependency arrows based on parsed data

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

<style>
table {
  border-collapse: collapse;
  width: 100%;
}

th,
td {
  border: 1px solid black;
  padding: 8px;
  text-align: left;
}

.container {
    display: flex;
    flex-direction: horizontal;
}

.course-card {
    width: 80px;
    padding: 5px;
}
</style>

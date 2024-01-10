<template>
  <div id="app">
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
import { ref, onMounted, computed } from 'vue';
import { parse } from './parser/parser.js';

// TODO rendering dependency arrows based on parsed data

const program = ref(null);
const courses = ref([]);

onMounted(async () => {
  try {
    const response = await fetch('data/programmes/EE1.json');
    const data = await response.json();
    program.value = data;
    courses.value = Object.values(data.courses).flat();
  } catch (error) {
    console.error(error);
  }
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

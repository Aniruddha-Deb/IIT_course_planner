<script setup>
import { ref, onMounted, computed, watch, getCurrentInstance } from 'vue';
import { And, Or, parse } from './parser/parser.js';
import { LinePath } from 'svg-dom-arrows';

const instance = getCurrentInstance();
const program = ref(null);
const courses = ref({});
const curr_courses = ref([]);
const selectedCourse = ref('AM1');
const renderDeps = ref(false);

const dep_arrows = ref([]);

async function update_course_db() {
  try {
    const response = await fetch(`data/courses_prereq_processed.json`);
    const data = await response.json();
    courses.value = data;
  } catch (error) {
    console.error(error);
  }
}

async function update_table(course) {
  try {
    const response = await fetch(`data/programmes/${course}.json`);
    const data = await response.json();
    program.value = data;
    curr_courses.value = new Set(data.recommended.flat());
    console.log(curr_courses.value);
  } catch (error) {
    console.error(error);
  }
}

watch(selectedCourse, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    renderDeps.value = false;
    toggle_deps();
    update_table(newValue);
  }
});

function createMarker() {
  const arrow = document.createElementNS("http://www.w3.org/2000/svg", 'path');
  const marker = document.createElementNS("http://www.w3.org/2000/svg", 'marker');

  arrow.setAttribute('d', 'M 0 0 L 10 5 L 0 10 z');
  arrow.setAttribute('style', 'fill:#ffffff55;stroke-width:0.801524;stroke-miterlimit:4;stroke-dasharray:none');

  marker.setAttribute('id', 'marker1'); // <== Make sure to set an id attribute
  /**
   * The below attributes and values are specific to this marker, you'll have to know how markers work
   * to really do something fun. For now you'll have to deal with it manually but I might work on an SVG
   * marker utility.
   */
  marker.setAttribute('refX', '5');
  marker.setAttribute('refY', '5');
  marker.setAttribute('viewBox', '0 0 10 10');
  marker.setAttribute('orient', 'auto-start-reverse'); // <== There is a trick here, be sure to read after the code snippet
  marker.setAttribute('markerWidth', '3');
  marker.setAttribute('markerHeight', '3');
  marker.appendChild(arrow);

  return marker;
};

function toggle_deps() {
  var newValue = renderDeps.value;
  if (newValue === true) {
    program.value.recommended.flat().forEach(item => {
      if (!(item in courses.value)) {
        return;
      }
      var deps = parse(courses.value[item].prereqs);
      // console.log(deps);
      // for now, just flatten the tree down. Will think about how to represent 
      // AND/OR later.
      var dep_courses = [];
      var stack = [deps];
      while (stack.length > 0) {
        const t = stack.pop();
        if (t instanceof And) {
          stack.push(t.left);
          stack.push(t.right);
        } 
        else if (t instanceof Or) {
          stack.push(t.left);
          stack.push(t.right);
        } 
        else if (typeof t === 'string') {
          dep_courses.push(t);
        }
      }
      dep_courses.forEach(dep => {
        if (!(curr_courses.value.has(dep))) {
          console.log(`${dep} not in curr_courses`);
          return;
        }
        var options = {
          start: {
            element: instance.refs[item][0],
            position: {
              top: 0,
              left: 0.5
            },
            markerId: '#marker1'
          },
          end: {
            element: instance.refs[dep][0],
            position: {
              top: 0.8,
              left: 0.5
            }
          },
          style: 'stroke:#ffffff55;stroke-width:4;fill:transparent',
          appendTo: document.body,
          markers: [createMarker()]
        }
        var linePath = new LinePath(options);
        linePath.containerDiv.style['pointer-events'] = 'none';
        dep_arrows.value.push(linePath);
      });
    });
  }
  else {
    console.log('removing arrows');
    dep_arrows.value.forEach(item => {
      item.containerDiv.remove();
    });
    dep_arrows.value.splice(0, dep_arrows.value.length);
  }
}

onMounted(async () => {
  update_table(selectedCourse.value);
  update_course_db();
});

const recommended = computed(() => {
  return program.value ? program.value.recommended : [];
});
</script>

<template>
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
  <label>
    <input type="checkbox" v-model="renderDeps" @change="toggle_deps">
    Render dependencies
  </label>
  <div class="course-container">
    <div class="course-row wrapper" v-for="(semester, index) in recommended" :key="index">
      <div class="course-label">Sem {{ index + 1 }}</div>
      <div class="course-cards container" v-dragula="semester" bag="schedule">
        <div class="course-card" :ref="courseCode" v-for="courseCode in semester" :key="courseCode">{{ courseCode }}</div>
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
  margin-top: 5px;
  margin-bottom: 5px;
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

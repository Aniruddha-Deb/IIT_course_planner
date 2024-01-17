<script setup>
import { ref, onMounted, computed, watch, getCurrentInstance } from 'vue';
import { And, Or, parse } from './parser/parser.js';
import LeaderLine from 'leader-line-new';
import { VueDragulaGlobal } from 'vue3-dragula';

// ? what do braces do in an import statement?

const instance = getCurrentInstance();
const program = ref(null);
const courses = ref({});
const curr_courses = ref([]);
const selectedCourse = ref('AM1');
const renderDeps = ref(false);

const dep_arrows = ref([]);
var arrow_map = new Map();
var current_course_dragged = null;
var drag_updater = null;

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

VueDragulaGlobal.eventBus.on('drag', function (el, container, source) {
  var drag_class = document.getElementsByClassName('gu-mirror')[0];
  console.log(drag_class);
  current_course_dragged = el[1].__vnode.key;
  if (renderDeps.value) {
    drag_updater = setInterval( () => {
      arrow_map.get(current_course_dragged).forEach(arrow => {
        arrow.path.position()
      });
    }, 50);
  }
});

VueDragulaGlobal.eventBus.on('dragend', function (el, container, source) {
  current_course_dragged = null;
  if (renderDeps.value) {
    clearInterval(drag_updater);
  }
});

function attach_course_arrows(code, div) {

}

function drop_course_arrows(code, div) {

}

// drag and drop:
// - Disconnect prior course arrows (both outward and inward)
// - Attach new course arrows 
// 
// TODO find a better representation of the graph... AND/OR might complicate?
// Just do this via an adjacency list graph. Won't need to recompute the edges

function get_course_deps(item) {
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
  return dep_courses;
}

function toggle_deps() {
  var newValue = renderDeps.value;
  if (newValue === true) {
    arrow_map = new Map();
    program.value.recommended.flat().forEach(item => {
      arrow_map.set(item, []);
    });
    program.value.recommended.flat().forEach(item => {
      if (!(item in courses.value)) {
        return;
      }
      var dep_courses = get_course_deps(item);
      dep_courses.forEach(dep => {
        if (!(curr_courses.value.has(dep))) {
          console.log(`${dep} not in curr_courses`);
          return;
        }
        var options = {
          color: '#ffffff55',
          path: 'straight'
        }
        var arrow_path = new LeaderLine(instance.refs[dep][0], instance.refs[item][0], options);
        var arrow = {
          src: dep,
          tgt: item,
          path: arrow_path
        }
        arrow_map.get(dep).push(arrow);
        arrow_map.get(item).push(arrow);
      });
    });
  }
  else {
    var all_arrows = [];
    arrow_map.forEach((value, key) => all_arrows.push(value));
    new Set(all_arrows.flat()).forEach(item => {
      item.path.remove();
    });
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

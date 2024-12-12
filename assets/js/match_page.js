const handleTeamChange = ($selector, key) => {
    const getTeamData = () => {
        const selectedValue = $selector.val(); // Получаем выбранное значение
        const processedValue = selectedValue ? Number(selectedValue) : null; // Преобразуем в число или null
        return { [key]: processedValue };
    }

    // Обработчик изменения
    $selector.on("change", function () {
        const payload = getTeamData();
        sendConstants(payload);
    });

    // Возвращаем функцию отправки, чтобы её можно было вызвать в произвольный момент
    return getTeamData;
};

const $left_team_selector = $("#team_left", document);
const $right_team_selector = $("#team_right", document);

// Привязываем обработчики изменения
const getLeftTeamData = handleTeamChange($left_team_selector, "team_left_id");
const getRightTeamData = handleTeamChange($right_team_selector, "team_right_id");

function toggleSelectors() {
    const isChecked = $team_auto_detect_input.checked;
    $left_team_selector.prop('disabled', isChecked);  // Отключаем или включаем первый селектор
    $right_team_selector.prop('disabled', isChecked);
    let payload = {'team_auto_detect': isChecked}
    if (!isChecked) {
        payload = Object.assign(payload, getLeftTeamData(), getRightTeamData())
    }
    sendConstants(payload)
}
const $team_auto_detect_input = document.getElementById('team_auto_detect');
$team_auto_detect_input.addEventListener('change', toggleSelectors);

// -----------------------------------------------------------------------------------------------

const $left_team_side_input = $("#left_team_side");
const $right_team_side_input = $("#right_team_side");
const $team_side_auto_detect_input = document.getElementById('team_side_auto_detect');

function toggleTeamSideInputs() {
    const isChecked = $team_side_auto_detect_input.checked;

    // Toggle the 'disabled' class based on the checkbox state
    $left_team_side_input.toggleClass('disabled', isChecked);
    $right_team_side_input.toggleClass('disabled', isChecked);

    let payload = { 'team_side_auto_detect': isChecked };
    if (!isChecked) {
        payload = Object.assign(payload, getTeamSideData());
    }

    sendConstants(payload);
}

$team_side_auto_detect_input.addEventListener('change', toggleTeamSideInputs);
const getTeamSideData = () => {
    const is_attack_left = $left_team_side_input.hasClass('team-t') && $right_team_side_input.hasClass('team-ct')
    const is_attack_right = $left_team_side_input.hasClass('team-ct') && $right_team_side_input.hasClass('team-t')
    if (!(is_attack_left || is_attack_right)) {
      throw new Error("ValueError: Invalid state");
    }
    const current_side = is_attack_left ? 'attack' : 'defence';
    return { "team_left_side": current_side };
}

const switchTeamSides = () => {
    $left_team_side_input.toggleClass('team-t');
    $left_team_side_input.toggleClass('team-ct');
    $right_team_side_input.toggleClass('team-t');
    $right_team_side_input.toggleClass('team-ct');
};

$left_team_side_input.click(function () {
    switchTeamSides();
    sendConstants(getTeamSideData());
});
$right_team_side_input.click(function () {
    switchTeamSides();
    sendConstants(getTeamSideData());
});

// -----------------------------------------------------------------------------------------------
const handleMapCounter = ($input, key) => {
    const mapCounterCircles = $input.find(".map-counter")
    const getMapCountData = () => {
        const visibleCircles = mapCounterCircles.filter(":visible");
        const activeCircles = visibleCircles.filter(".active");
        return activeCircles.length
    }
    const getMapCountPayload = () => {
        return {[key]: getMapCountData()}
    }

    const setActiveCountByValue = (map_count) => {
        const max_count = mapCounterCircles.filter(":visible").length;
        mapCounterCircles.map(function () {
            const circle = $(this)
            const circle_number = Number(
                circle.attr('id')
                .replace('left-circle-', '')
                .replace('right-circle-', '')
            );
            circle.toggleClass('active', ((circle_number <= map_count) && (circle_number <= max_count)));
        });
    }

    const setVisibleCountByValue = (circle_count) => {
        mapCounterCircles.map(function () {
            const circle = $(this)
            const circle_number = Number(
                circle.attr('id')
                    .replace('left-circle-', '')
                    .replace('right-circle-', '')
            );
            circle.prop('hidden', circle_number > circle_count);
        });
    }

    $input.click( function () {
        const max_count = mapCounterCircles.filter(":visible").length;
        const next_map_count = getMapCountData() + 1;
        next_map_count <= max_count ? setActiveCountByValue(next_map_count) : setActiveCountByValue(0)
        sendConstants(getMapCountPayload())
    });

    // Возвращаем функцию отправки, чтобы её можно было вызвать в произвольный момент
    return {
        getMapCountData,
        getMapCountPayload,
        setActiveCountByValue,
        setVisibleCountByValue,
    };
};

const leftMapCounterHandler = handleMapCounter($('#left-map-counter'), 'left_team_map_count');
const rightMapCounterHandler = handleMapCounter($('#right-map-counter'), 'right_team_map_count');
const mapCountersBlock = $('#map-counters-block');
$("#btn-match-type-bo1, #btn-match-type-bo3, #btn-match-type-bo5").click(function () {
    const match_type = this.id.replace('btn-match-type-', ''),
          left_map_count = leftMapCounterHandler.getMapCountData(),
          right_map_count = rightMapCounterHandler.getMapCountData();
    mapCountersBlock.toggleClass('d-none', match_type === 'bo1');

    let payload = { match_type , 'left_team_map_count': 0, 'right_team_map_count': 0};

    if (['bo3', 'bo5'].includes(match_type)) {
        const visibleCount = match_type === 'bo3' ? 2 : 3;
        leftMapCounterHandler.setVisibleCountByValue(visibleCount);
        rightMapCounterHandler.setVisibleCountByValue(visibleCount);
        leftMapCounterHandler.setActiveCountByValue(left_map_count);
        rightMapCounterHandler.setActiveCountByValue(right_map_count);
        payload = {
            ...payload,
            ...leftMapCounterHandler.getMapCountPayload(),
            ...rightMapCounterHandler.getMapCountPayload()
        };
    }
    sendConstants(payload);
});



const handleTeamChange = ($selector, key) => {
    const getTeamData = () => {
        const selectedValue = $selector.val(); // Получаем выбранное значение
        const processedValue = selectedValue ? Number(selectedValue) : null; // Преобразуем в число или null
        return { [key]: processedValue };
    }
    // Функция отправки данных
    const sendTeamData = () => {
        const payload = getTeamData();
        console.log('Sending payload:', payload); // Логируем payload
        sendConstants(payload); // Отправляем данные
    };

    // Обработчик изменения
    $selector.on("change", function () {
        sendTeamData(); // Отправляем данные при изменении
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
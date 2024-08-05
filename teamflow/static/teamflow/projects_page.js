async function fetchProjects() {
    try {
        const response = await fetch('/api/projects/user');
        const data = await response.json();
        const projectsDiv = document.querySelector('.projects');
        
        // Limpar qualquer conteúdo existente na div
        projectsDiv.innerHTML = '';

        // Iterar sobre cada projeto e construir o HTML
        data.forEach(project => {
            // Criar o HTML para o projeto
            const projectHTML = `
                <div class="project">
                    <h3><a href="/projects/${project.id}/">${project.name}</a></h3>
                    <p><strong>Description:</strong> ${project.description}</p>
                    <p><strong>Start Date:</strong> ${project.start_date}</p>
                    <p><strong>Due Date:</strong> ${project.due_date}</p>
                </div>
                <hr>
            `;

            // Adicionar o HTML do projeto à div de projetos
            projectsDiv.innerHTML += projectHTML;
        });
    } catch (error) {
        console.error('Error fetching projects:', error);
    }
}

document.addEventListener('DOMContentLoaded', fetchProjects);

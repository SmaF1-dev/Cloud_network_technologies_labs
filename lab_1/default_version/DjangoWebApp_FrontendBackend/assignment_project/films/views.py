from django.shortcuts import render
from django.db import connection
from django.views import View

# Create your views here.

class FilmDashboardView(View):
    """
    View to display the films dashboard.
    Fetches data for various charts to provide insights about films database.
    
    """
    def get(self, request):
        """
        Handles GET request to render the films dashboard.
        
        Queries the database to gather data for different charts, including:
            - A bar chart showing the top 10 most rented films, ordered by rental counts, along with their rental counts and total revenue.
            - A pie chart displaying the total revenue for each of the top 10 films and their percentage contribution to the overall revenue.
            - A line chart presenting the total revenue for each month to show revenue trends over time.
            - A clustered bar chart displaying the count of films grouped by language and category.
            - A donut chart showing the number of unique customers per category and their percentage share of the total unique customers.
            - A scatter plot comparing revenue and rental counts for each category, with average revenue per rental calculated for each category.

        Returns:
            HttpResponse: Renders the 'films/dashboard.html' template with chart data.
        """
        # Query for bar chart: Top 10 most rented films with rental count and total revenue)
        bar_chart_query = """
        SELECT film.title,
               COUNT(rental.rental_id) AS rental_count,
               ROUND(SUM(payment.amount), 2) AS total_revenue
        FROM rental
        INNER JOIN inventory ON rental.inventory_id = inventory.inventory_id
        INNER JOIN film ON inventory.film_id = film.film_id
        INNER JOIN payment ON rental.rental_id = payment.rental_id
        GROUP BY film.title
        ORDER BY rental_count DESC
        LIMIT 10;
        """
        # bar_chart_query explanation:
        # - Retrieves film titles, counts how many times each film was rented (rental count), and calculates the total revenue from rentals.
        # - Groups the data by film title, orders by rental count in descending order, and limits the results to the top 10 films.
        
        with connection.cursor() as cursor:
            cursor.execute(bar_chart_query)
            bar_chart_results = cursor.fetchall()

        # Prepare data for the bar chart
        bar_chart_data = {
            "titles": [row[0] for row in bar_chart_results],
            "rental_counts": [row[1] for row in bar_chart_results],
            "total_revenues": [float(row[2]) for row in bar_chart_results],
        }

        # Query for pie chart: Top 10 films by revenue contribution
        pie_chart_query = """
        SELECT film.title,
               ROUND(SUM(payment.amount), 2) AS total_revenue,
               (SUM(payment.amount) / (SELECT SUM(payment.amount) FROM payment)) * 100 AS revenue_percentage
        FROM payment
        INNER JOIN rental ON payment.rental_id = rental.rental_id
        INNER JOIN inventory ON rental.inventory_id = inventory.inventory_id
        INNER JOIN film ON inventory.film_id = film.film_id
        GROUP BY film.title
        ORDER BY total_revenue DESC
        LIMIT 10;
        """
        # Pie_chart_query explanation:
        # - Retrieves film titles and their total revenue from payments.
        # - Calculates each film's revenue as a percentage of the total revenue generated across all films.
        # - Groups the data by film title, orders by revenue in descending order, and limits to the top 10 films.

        with connection.cursor() as cursor:
            cursor.execute(pie_chart_query)
            pie_chart_results = cursor.fetchall()
        
        # Prepare data for the pie chart
        pie_chart_data = {
            "titles": [row[0] for row in pie_chart_results],
            "total_revenues": [float(row[1]) for row in pie_chart_results],
            "percentages": [f"{round(row[2], 2)}%" for row in pie_chart_results],
        }
        
        # Query for line chart: Monthly Revenue Trends
        line_chart_query = """
        SELECT
            DATE_FORMAT(payment.payment_date, '%Y-%m') AS month,
            ROUND(SUM(payment.amount), 2) AS total_revenue
        FROM
            payment
        GROUP BY month
        ORDER BY month;
        """
        # line_char_query explanation:
        # - Extracts the year and month from payment dates, then sums the revenue for each month.
        # - Groups the data by month and orders the results chronologically to show revenue trends over time.

        with connection.cursor() as cursor:
            cursor.execute(line_chart_query)
            line_chart_results = cursor.fetchall()

        # Prepare data for the line chart
        line_chart_data = {
            "months": [row[0] for row in line_chart_results],
            "total_revenues": [float(row[1]) for row in line_chart_results],
        }
    
        # Query for clustered bar chart: Total Films by Language and Category
        clustered_bar_chart_query = """
        SELECT
            category.name AS category_name,
            language.name AS language_name,
            COUNT(film.film_id) AS film_count
        FROM
            film
        INNER JOIN film_category ON film.film_id = film_category.film_id
        INNER JOIN category ON film_category.category_id = category.category_id
        INNER JOIN language ON film.language_id = language.language_id
        GROUP BY category.name, language.name
        ORDER BY film_count DESC;
        """
        # clustered_bar_chart_query explanation:
        # - Retrieves the names of film categories and languages, and counts how many films belong to each combination of category and language.
        # - Groups the data by category and language, and orders by the number of films in descending order.

        with connection.cursor() as cursor:
            cursor.execute(clustered_bar_chart_query)
            clustered_bar_chart_results = cursor.fetchall()

        # Prepare data for the clustered bar chart
        categories = {}
        languages = set()

        for row in clustered_bar_chart_results:
            category_name = row[0]
            language_name = row[1]
            film_count = row[2]

            languages.add(language_name)
            if category_name not in categories:
                categories[category_name] = {}
            categories[category_name][language_name] = film_count

        # Organize data for Chart.js
        languages = sorted(languages)
        clustered_bar_chart_data = {
            "categories": list(categories.keys()),
            "languages": languages,
            "data": [
                [categories[category].get(language, 0) for language in languages]
                for category in categories
            ],
        }

        # Query for donut chart: Unique Customer Preferences by Category
        donut_chart_query = """
        SELECT
            category.name AS category_name,
            COUNT(DISTINCT customer.customer_id) AS customer_count,
            ROUND((COUNT(DISTINCT customer.customer_id) / (SELECT COUNT(DISTINCT customer.customer_id) FROM customer)) * 100, 2) AS customer_percentage
        FROM
            customer
        INNER JOIN rental ON customer.customer_id = rental.customer_id
        INNER JOIN inventory ON rental.inventory_id = inventory.inventory_id
        INNER JOIN film ON inventory.film_id = film.film_id
        INNER JOIN film_category ON film.film_id = film_category.film_id
        INNER JOIN category ON film_category.category_id = category.category_id
        GROUP BY category.name
        ORDER BY customer_count DESC;
        """
        # donut_chart_query explanation:
        # - Retrieves film categories and counts the number of unique customers who rented films from each category.
        # - Calculates the percentage of the total unique customers that rented films from each category.
        # - Groups the data by category, orders by customer count in descending order, and shows the top categories.

        with connection.cursor() as cursor:
            cursor.execute(donut_chart_query)
            donut_chart_results = cursor.fetchall()

        # Prepare data for the donut chart
        donut_chart_data = {
            "categories": [row[0] for row in donut_chart_results],
            "customer_counts": [int(row[1]) for row in donut_chart_results],
            "percentages": [float(row[2]) for row in donut_chart_results],
        }

        # Query for scatter plot: Revenue vs. Rentals by Category
        scatter_plot_query = """
        SELECT
            category.name AS category_name,
            COUNT(rental.rental_id) AS rental_count,
            ROUND(SUM(payment.amount), 2) AS total_revenue,
            ROUND(SUM(payment.amount) / COUNT(rental.rental_id), 2) AS avg_revenue_per_rental
        FROM category
        INNER JOIN film_category ON category.category_id = film_category.category_id
        INNER JOIN film ON film_category.film_id = film.film_id
        INNER JOIN inventory ON film.film_id = inventory.film_id
        INNER JOIN rental ON inventory.inventory_id = rental.inventory_id
        INNER JOIN payment ON rental.rental_id = payment.rental_id
        GROUP BY category.name
        ORDER BY total_revenue DESC;
        """
        # scatter_plot_query explanation:
        # - Retrieves film categories and calculates the number of rentals and total revenue for each category.
        # - Computes the average revenue per rental for each category.
        # - Groups the data by category, orders by total revenue in descending order, and presents a comparison of revenue vs. rental counts.

        with connection.cursor() as cursor:
            cursor.execute(scatter_plot_query)
            scatter_plot_results = cursor.fetchall()

        # Prepare data for the scatter plot
        scatter_plot_data = {
            "categories": [row[0] for row in scatter_plot_results],
            "rental_counts": [row[1] for row in scatter_plot_results],
            "total_revenues": [float(row[2]) for row in scatter_plot_results],
            "avg_revenue_per_rentals": [round(float(row[2]) / row[1], 2) if row[1] > 0 else 0 for row in scatter_plot_results], # "round(float(row[2]) / row[1], 2) if row[1] > 0 else 0" ensures no division by zero
        }

        return render(request, 'films/dashboard.html', {
            'bar_chart_data': bar_chart_data,
            'pie_chart_data': pie_chart_data,
            'line_chart_data': line_chart_data,
            'clustered_bar_chart_data': clustered_bar_chart_data,
            'donut_chart_data': donut_chart_data,
            'scatter_plot_data': scatter_plot_data,
        })